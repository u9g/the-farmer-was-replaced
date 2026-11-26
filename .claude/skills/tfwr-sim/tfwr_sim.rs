#!/usr/bin/env -S cargo +nightly -Zscript
---cargo
[package]
edition = "2021"

[profile.dev]
opt-level = 3
debug-assertions = false
overflow-checks = false
codegen-units = 1
lto = "fat"
incremental = false
panic = "abort"
---
// tfwr_sim.rs - The Farmer Was Replaced, reimplemented as a headless one-file Rust harness.
//
// This is a port of the game's own code (decompiled Core.dll / Utils.dll), not an approximation:
// the tokenizer, parser, tree-walking interpreter (each drone's program runs as plain recursion on a
// stack of its own, a fiber, and steps out to the scheduler exactly where the game's C# iterators
// yield),
// per-drone op counting, Execution.Execute scheduling loop, Simulation timers, Farm, grid, drones,
// plants (grass, bush, tree, carrot, pumpkin, sunflower, cactus), mazes, the dinosaur hat, water,
// fertilizer, power, polyculture, unlocks and System.Random are translated function by function.
// Function and variable names follow the C# so the two can be compared side by side.
//
// Run it as a script from the save folder (nightly Rust, no crates; cargo builds it once into its
// own cache, not next to this file):
//     cargo +nightly -Zscript path/to/tfwr_sim.rs cactus.py --seeds 8 --quiet
//     cargo +nightly -Zscript path/to/tfwr_sim.rs cactus.py cactus_new.py --seed 1 --seeds 8 --quiet
//     cargo +nightly -Zscript path/to/tfwr_sim.rs pumpkins.py --item pumpkin --seed 7
//     cargo +nightly -Zscript path/to/tfwr_sim.rs --help
// It reads unlock levels and items from save.json next to the script it runs.
//
// Not ported (the script stops with an error if it reaches one): the mining DLC (dig, push, place,
// hover, prospect_*, jump, bamboo, rice, dynamite, mushrooms, underground world generation),
// simulate() and leaderboard_run() called from a script (a leaderboard attempt is run from the
// command line instead: --leaderboard, or give the launcher script), the "feature not unlocked yet" checks on language keywords, and
// anything that is only visual or audio. The farm starts as a freshly generated field.
#![allow(dead_code, unused_variables, unused_mut, unused_assignments, non_snake_case, non_upper_case_globals)]
#![allow(clippy::all)]

use std::cell::{Cell, RefCell};
use std::collections::{HashMap, HashSet, VecDeque};
use std::rc::Rc;

type R<T> = Result<T, String>;

/// FxHash (rustc's hasher): far cheaper than the default SipHash for the short keys of variable
/// tables and dict indexes. Only lookups use it; iteration order comes from insertion order.
#[derive(Default, Clone, Copy)]
struct Fx(u64);
impl std::hash::Hasher for Fx {
    #[inline]
    fn write(&mut self, bytes: &[u8]) {
        let mut b = bytes;
        while b.len() >= 8 {
            self.add(u64::from_le_bytes(b[..8].try_into().unwrap()));
            b = &b[8..];
        }
        if b.len() >= 4 {
            self.add(u32::from_le_bytes(b[..4].try_into().unwrap()) as u64);
            b = &b[4..];
        }
        for &x in b {
            self.add(x as u64);
        }
    }
    #[inline]
    fn write_u8(&mut self, i: u8) {
        self.add(i as u64);
    }
    #[inline]
    fn write_u32(&mut self, i: u32) {
        self.add(i as u64);
    }
    #[inline]
    fn write_u64(&mut self, i: u64) {
        self.add(i);
    }
    #[inline]
    fn write_usize(&mut self, i: usize) {
        self.add(i as u64);
    }
    #[inline]
    fn finish(&self) -> u64 {
        self.0
    }
}
impl Fx {
    #[inline]
    fn add(&mut self, w: u64) {
        self.0 = (self.0.rotate_left(5) ^ w).wrapping_mul(0x51_7c_c1_b7_27_22_0a_95);
    }
}
type FxBuild = std::hash::BuildHasherDefault<Fx>;
type FxMap<K, V> = HashMap<K, V, FxBuild>;

thread_local! {
    static NAMES: RefCell<HashSet<Rc<str>, FxBuild>> = RefCell::new(HashSet::default());
}
/// The one shared copy of a name. Every name that reaches a variable table is interned (the parser
/// interns identifiers; builtins and `__name__` are interned where they are registered), so the
/// tables can key on the string's address instead of hashing and comparing its text.
fn intern(s: &str) -> Rc<str> {
    NAMES.with(|n| {
        let mut n = n.borrow_mut();
        if let Some(r) = n.get(s) {
            return r.clone();
        }
        let r: Rc<str> = Rc::from(s);
        n.insert(r.clone());
        r
    })
}
#[inline]
fn name_key(name: &str) -> usize {
    name.as_ptr() as usize
}
#[inline]
fn bloom_bit(key: usize) -> u64 {
    1u64 << (((key >> 4) ^ (key >> 10)) & 63)
}

/// Every drone's program runs on a stack of its own, so the interpreter can be plain recursion
/// that steps out to the scheduler wherever the game's iterators would yield, without a heap
/// coroutine per syntax node. Windows has fibers for this; elsewhere each drone gets a thread and
/// the two take turns (correct, only slower).
mod stacks {
    #[cfg(windows)]
    mod imp {
        use std::cell::Cell;
        use std::ffi::c_void;
        #[link(name = "kernel32")]
        extern "system" {
            fn ConvertThreadToFiber(param: *mut c_void) -> *mut c_void;
            fn CreateFiberEx(commit: usize, reserve: usize, flags: u32, start: extern "system" fn(*mut c_void), param: *mut c_void) -> *mut c_void;
            fn SwitchToFiber(fiber: *mut c_void);
            fn DeleteFiber(fiber: *mut c_void);
        }
        thread_local! {
            /// the scheduler's own fiber on this thread
            static MAIN: Cell<*mut c_void> = const { Cell::new(std::ptr::null_mut()) };
        }
        struct Start {
            body: Option<Box<dyn FnOnce()>>,
            done: Cell<bool>,
        }
        pub struct Stack {
            fiber: *mut c_void,
            start: *mut Start,
        }
        extern "system" fn trampoline(p: *mut c_void) {
            let start = p as *mut Start;
            let body = unsafe { (*start).body.take() };
            if let Some(body) = body {
                body();
            }
            unsafe { (*start).done.set(true) };
            // A fiber must never return: that would end the thread.
            loop {
                suspend();
            }
        }
        impl Stack {
            pub fn new(body: Box<dyn FnOnce()>) -> Stack {
                MAIN.with(|m| {
                    if m.get().is_null() {
                        let f = unsafe { ConvertThreadToFiber(std::ptr::null_mut()) };
                        assert!(!f.is_null(), "ConvertThreadToFiber failed");
                        m.set(f);
                    }
                });
                let start = Box::into_raw(Box::new(Start { body: Some(body), done: Cell::new(false) }));
                // The interpreter recurses with the script's call depth: reserve a deep stack
                // (address space only; pages are committed as they are touched).
                let fiber = unsafe { CreateFiberEx(64 << 10, 256 << 20, 0, trampoline, start as *mut c_void) };
                assert!(!fiber.is_null(), "CreateFiberEx failed");
                Stack { fiber, start }
            }
            /// Runs the program until it calls suspend() or ends.
            pub fn resume(&self) {
                unsafe { SwitchToFiber(self.fiber) };
            }
            pub fn done(&self) -> bool {
                unsafe { (*self.start).done.get() }
            }
        }
        impl Drop for Stack {
            fn drop(&mut self) {
                // Whatever an unfinished program still holds on its stack is leaked, not dropped.
                unsafe {
                    DeleteFiber(self.fiber);
                    drop(Box::from_raw(self.start));
                }
            }
        }
        /// Called by a running program: back to the scheduler.
        pub fn suspend() {
            let main = MAIN.with(|m| m.get());
            unsafe { SwitchToFiber(main) };
        }
    }

    #[cfg(not(windows))]
    mod imp {
        use std::cell::RefCell;
        use std::sync::{Arc, Condvar, Mutex};
        /// whose turn it is: false the scheduler's, true the program's
        struct Baton {
            turn: Mutex<(bool, bool)>, // (program's turn, program done)
            cv: Condvar,
        }
        struct SendBox(Box<dyn FnOnce()>);
        unsafe impl Send for SendBox {}
        thread_local! {
            static CURRENT: RefCell<Option<Arc<Baton>>> = const { RefCell::new(None) };
        }
        pub struct Stack {
            baton: Arc<Baton>,
            thread: Option<std::thread::JoinHandle<()>>,
        }
        impl Stack {
            pub fn new(body: Box<dyn FnOnce()>) -> Stack {
                let baton = Arc::new(Baton { turn: Mutex::new((false, false)), cv: Condvar::new() });
                let b = baton.clone();
                let body = SendBox(body);
                let thread = std::thread::Builder::new()
                    .stack_size(256 << 20)
                    .spawn(move || {
                        let body = body;
                        {
                            let mut t = b.turn.lock().unwrap();
                            while !t.0 {
                                t = b.cv.wait(t).unwrap();
                            }
                        }
                        CURRENT.with(|c| *c.borrow_mut() = Some(b.clone()));
                        (body.0)();
                        let mut t = b.turn.lock().unwrap();
                        *t = (false, true);
                        b.cv.notify_all();
                    })
                    .expect("cannot start a drone thread");
                Stack { baton, thread: Some(thread) }
            }
            pub fn resume(&self) {
                let mut t = self.baton.turn.lock().unwrap();
                if t.1 {
                    return;
                }
                t.0 = true;
                self.baton.cv.notify_all();
                while t.0 {
                    t = self.baton.cv.wait(t).unwrap();
                }
            }
            pub fn done(&self) -> bool {
                self.baton.turn.lock().unwrap().1
            }
        }
        impl Drop for Stack {
            fn drop(&mut self) {
                // An unfinished program's thread stays parked forever; it holds nothing shared.
                if self.done() {
                    if let Some(t) = self.thread.take() {
                        let _ = t.join();
                    }
                }
            }
        }
        pub fn suspend() {
            let b = CURRENT.with(|c| c.borrow().clone()).expect("suspend outside a drone");
            let mut t = b.turn.lock().unwrap();
            t.0 = false;
            b.cv.notify_all();
            while !t.0 {
                t = b.cv.wait(t).unwrap();
            }
        }
    }
    pub use imp::{suspend, Stack};
}

/// Small-block allocator: the interpreter makes millions of short-lived allocations per run (one
/// boxed coroutine per node it evaluates), and the Windows heap spends about half of all run time
/// on them. Blocks up to 8 KiB come from per-thread free lists of size classes, carved from 256 KiB
/// chunks that are never handed back; anything bigger goes to the system allocator.
/// A block freed on another thread joins that thread's list, which is fine: memory is memory.
mod pool {
    use std::alloc::{GlobalAlloc, Layout, System};
    use std::cell::UnsafeCell;
    // 16-byte classes up to 512 bytes, then 256-byte classes up to 8 KiB (a node's coroutine is
    // several hundred bytes to a few KiB).
    const CLASSES: usize = 62;
    const MAX: usize = 8192;
    const CHUNK: usize = 256 * 1024;
    struct Lists {
        free: [*mut u8; CLASSES],
    }
    thread_local! {
        static LISTS: UnsafeCell<Lists> = const { UnsafeCell::new(Lists { free: [std::ptr::null_mut(); CLASSES] }) };
    }
    pub struct Pool;
    #[inline(always)]
    fn class(l: &Layout) -> Option<usize> {
        let n = l.size();
        if n == 0 || n > MAX || l.align() > 16 {
            None
        } else if n <= 512 {
            Some((n - 1) >> 4)
        } else {
            Some(30 + ((n - 1) >> 8))
        }
    }
    #[cold]
    unsafe fn refill(lists: &mut Lists, c: usize) {
        let size = if c < 32 { (c + 1) * 16 } else { (c - 29) << 8 };
        let chunk = System.alloc(Layout::from_size_align_unchecked(CHUNK, 16));
        if chunk.is_null() {
            return;
        }
        let n = CHUNK / size;
        for i in (0..n).rev() {
            let p = chunk.add(i * size);
            *(p as *mut *mut u8) = lists.free[c];
            lists.free[c] = p;
        }
    }
    unsafe impl GlobalAlloc for Pool {
        #[inline(always)]
        unsafe fn alloc(&self, l: Layout) -> *mut u8 {
            match class(&l) {
                Some(c) => LISTS
                    .try_with(|cell| {
                        let lists = &mut *cell.get();
                        if lists.free[c].is_null() {
                            refill(lists, c);
                            if lists.free[c].is_null() {
                                return std::ptr::null_mut();
                            }
                        }
                        let p = lists.free[c];
                        lists.free[c] = *(p as *mut *mut u8);
                        p
                    })
                    .unwrap_or_else(|_| System.alloc(Layout::from_size_align_unchecked(MAX, 16))),
                None => System.alloc(l),
            }
        }
        #[inline(always)]
        unsafe fn dealloc(&self, p: *mut u8, l: Layout) {
            match class(&l) {
                Some(c) => {
                    // During thread teardown the list is gone; the block is simply leaked.
                    let _ = LISTS.try_with(|cell| {
                        let lists = &mut *cell.get();
                        *(p as *mut *mut u8) = lists.free[c];
                        lists.free[c] = p;
                    });
                }
                None => System.dealloc(p, l),
            }
        }
    }
    #[global_allocator]
    static GLOBAL: Pool = Pool;
}

const ACTION_OPS: f64 = 200.0;
const OPERATION_OPS: f64 = 1.0;

// ---------------------------------------------------------------------------------------------
// System.Random (the seeded subtractive generator used by Mono and .NET's compatibility mode)
// ---------------------------------------------------------------------------------------------
struct SysRandom {
    seed_array: [i32; 56],
    inext: usize,
    inextp: usize,
}

impl SysRandom {
    fn new(seed: i32) -> SysRandom {
        let mut sa = [0i32; 56];
        let subtraction = if seed == i32::MIN { i32::MAX } else { seed.abs() };
        let mut mj = 161803398i32.wrapping_sub(subtraction);
        sa[55] = mj;
        let mut mk = 1i32;
        for i in 1..55 {
            let ii = (21 * i) % 55;
            sa[ii] = mk;
            mk = mj.wrapping_sub(mk);
            if mk < 0 {
                mk = mk.wrapping_add(i32::MAX);
            }
            mj = sa[ii];
        }
        for _ in 1..5 {
            for i in 1..56 {
                sa[i] = sa[i].wrapping_sub(sa[1 + (i + 30) % 55]);
                if sa[i] < 0 {
                    sa[i] = sa[i].wrapping_add(i32::MAX);
                }
            }
        }
        SysRandom { seed_array: sa, inext: 0, inextp: 21 }
    }
    fn internal_sample(&mut self) -> i32 {
        let mut loc_inext = self.inext + 1;
        if loc_inext >= 56 {
            loc_inext = 1;
        }
        let mut loc_inextp = self.inextp + 1;
        if loc_inextp >= 56 {
            loc_inextp = 1;
        }
        let mut ret = self.seed_array[loc_inext].wrapping_sub(self.seed_array[loc_inextp]);
        if ret == i32::MAX {
            ret -= 1;
        }
        if ret < 0 {
            ret = ret.wrapping_add(i32::MAX);
        }
        self.seed_array[loc_inext] = ret;
        self.inext = loc_inext;
        self.inextp = loc_inextp;
        ret
    }
    fn sample(&mut self) -> f64 {
        self.internal_sample() as f64 * (1.0 / i32::MAX as f64)
    }
    fn next(&mut self) -> i32 {
        self.internal_sample()
    }
    fn next_max(&mut self, max: i32) -> i32 {
        (self.sample() * max as f64) as i32
    }
    fn next_range(&mut self, min: i32, max: i32) -> i32 {
        let range = max as i64 - min as i64;
        (self.sample() * range as f64) as i32 + min
    }
    fn next_double(&mut self) -> f64 {
        self.sample()
    }
    fn next_bytes(&mut self, buf: &mut [u8]) {
        for b in buf.iter_mut() {
            *b = (self.internal_sample() % 256) as u8;
        }
    }
}

fn sha256(data: &[u8]) -> [u8; 32] {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98,
        0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
        0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8,
        0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819,
        0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
        0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
        0xc67178f2,
    ];
    let mut h: [u32; 8] =
        [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    let mut msg = data.to_vec();
    let bit_len = (data.len() as u64) * 8;
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bit_len.to_be_bytes());
    for chunk in msg.chunks(64) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([chunk[4 * i], chunk[4 * i + 1], chunk[4 * i + 2], chunk[4 * i + 3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16].wrapping_add(s0).wrapping_add(w[i - 7]).wrapping_add(s1);
        }
        let mut v = h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7].wrapping_add(s1).wrapping_add(ch).wrapping_add(K[i]).wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v[7] = v[6];
            v[6] = v[5];
            v[5] = v[4];
            v[4] = v[3].wrapping_add(t1);
            v[3] = v[2];
            v[2] = v[1];
            v[1] = v[0];
            v[0] = t1.wrapping_add(t2);
        }
        for i in 0..8 {
            h[i] = h[i].wrapping_add(v[i]);
        }
    }
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4 * i..4 * i + 4].copy_from_slice(&h[i].to_be_bytes());
    }
    out
}

/// Helper.JustSha256It
fn just_sha256_it(random: &mut SysRandom) -> i32 {
    let mut buffer = [0u8; 16];
    random.next_bytes(&mut buffer);
    let hash = sha256(&buffer);
    i32::from_le_bytes([hash[0], hash[1], hash[2], hash[3]]) & 0x7FFFFFFF
}

// Duration: nanoseconds as i64, with the same truncating arithmetic as the C# struct.
fn dur_from_seconds(seconds: f64) -> i64 {
    (seconds * 1000000000.0) as i64
}
fn dur_mul(a: i64, b: f64) -> i64 {
    (a as f64 * b) as i64
}
fn dur_seconds(a: i64) -> f64 {
    a as f64 / 1000000000.0
}

/// System.Collections.Generic.PriorityQueue (quaternary heap, same sift rules, so equal
/// priorities come out in the same order as in the game).
struct PriorityQueue<T> {
    nodes: Vec<(T, i64)>,
}

impl<T: Clone> PriorityQueue<T> {
    fn new() -> Self {
        PriorityQueue { nodes: Vec::new() }
    }
    fn enqueue(&mut self, element: T, priority: i64) {
        let node = (element, priority);
        self.nodes.push(node.clone());
        let mut idx = self.nodes.len() - 1;
        while idx > 0 {
            let parent = (idx - 1) >> 2;
            if node.1 >= self.nodes[parent].1 {
                break;
            }
            self.nodes[idx] = self.nodes[parent].clone();
            idx = parent;
        }
        self.nodes[idx] = node;
    }
    fn peek(&self) -> Option<&(T, i64)> {
        self.nodes.first()
    }
    fn dequeue(&mut self) -> Option<(T, i64)> {
        if self.nodes.is_empty() {
            return None;
        }
        let root = self.nodes[0].clone();
        let node = self.nodes.pop().unwrap();
        let size = self.nodes.len();
        if size > 0 {
            let mut idx = 0usize;
            loop {
                let first = (idx << 2) + 1;
                if first >= size {
                    break;
                }
                let mut min_child = first;
                let upper = (first + 4).min(size);
                let mut i = first + 1;
                while i < upper {
                    if self.nodes[i].1 < self.nodes[min_child].1 {
                        min_child = i;
                    }
                    i += 1;
                }
                if node.1 <= self.nodes[min_child].1 {
                    break;
                }
                self.nodes[idx] = self.nodes[min_child].clone();
                idx = min_child;
            }
            self.nodes[idx] = node;
        }
        Some(root)
    }
}

// ---------------------------------------------------------------------------------------------
// Values (IPyObject and friends)
// ---------------------------------------------------------------------------------------------
const NS_ENTITIES: u8 = 0;
const NS_ITEMS: u8 = 1;
const NS_GROUNDS: u8 = 2;
const NS_UNLOCKS: u8 = 3;
const NS_HATS: u8 = 4;
const NS_LEADERBOARDS: u8 = 5;
static NS_NAMES: [&str; 6] = ["Entities", "Items", "Grounds", "Unlocks", "Hats", "Leaderboards"];

static ITEM_NAMES: &[&str] = &[
    "bamboo", "block", "bone", "cactus", "carrot", "coal", "dynamite", "fertilizer", "gold", "hay", "iron",
    "mushroom", "piggy", "power", "pumpkin", "quartz", "rice", "water", "weird_substance", "wood",
];
/// Guesses the item a script farms from the start of its file name, so `maze1.py`,
/// `pumpkins2drones.py` and `cactus_v2.py` report gold, pumpkin and cactus.
fn item_from_stem(stem: &str) -> Option<String> {
    const ALIASES: &[(&str, &str)] = &[
        ("maze", "gold"), ("treasure", "gold"), ("dinosaur", "bone"), ("dino", "bone"),
        ("wheat", "hay"), ("grass", "hay"), ("tree", "wood"), ("bush", "wood"),
        ("weird", "weird_substance"), ("sunflower", "power"),
    ];
    let stem = stem.to_ascii_lowercase();
    let mut names: Vec<(&str, &str)> = ITEM_NAMES.iter().map(|n| (*n, *n)).chain(ALIASES.iter().copied()).collect();
    names.sort_by_key(|(prefix, _)| std::cmp::Reverse(prefix.len()));
    names.into_iter().find(|(prefix, _)| stem.starts_with(prefix)).map(|(_, item)| item.to_string())
}
static GROUND_NAMES: &[&str] = &[
    "basalt", "bedrock", "block_blue", "block_green", "block_red", "clay", "coal", "dirt", "dry_rice_terrace",
    "dynamite", "grassland", "iron", "limestone", "loam", "perlite", "petrified_pumpkin", "quartz", "rice_terrace",
    "rock", "sand", "soil", "soot", "treasure_goal", "treasure_map", "treasure_path",
];
static HAT_NAMES: &[&str] = &[
    "bamboo_hat", "brown_hat", "bucket", "cactus_hat", "carrot_hat", "coal_hat", "dinosaur_hat", "dynamite_hat",
    "explosive_drill", "gold_hat", "gold_trophy_hat", "golden_cactus_hat", "golden_carrot_hat", "golden_gold_hat",
    "golden_pumpkin_hat", "golden_sunflower_hat", "golden_tree_hat", "gray_hat", "green_hat", "low_orbit_potato",
    "mining_hat", "mushroom_hat", "olexas_hood", "pumpkin_hat", "purple_hat", "quartz_hat", "rice_hat",
    "silver_trophy_hat", "straw_hat", "sunflower_hat", "the_farmers_remains", "top_hat", "traffic_cone",
    "traffic_cone_stack", "tree_hat", "wizard_hat", "wood_trophy_hat",
];
static LEADERBOARD_NAMES: &[&str] = &[
    "bamboo", "bamboo_single", "cactus", "cactus_single", "carrots", "carrots_single", "dinosaur", "dynamite",
    "dynamite_single", "fastest_reset", "fastest_underground_reset", "hay", "hay_single", "maze", "maze_single",
    "mushrooms", "mushrooms_single", "ores", "ores_single", "pumpkins", "pumpkins_single", "pyramids",
    "pyramids_single", "rice", "rice_single", "sunflowers", "sunflowers_single", "treasure_map", "wood",
    "wood_single",
];

fn ns_members(ns: u8) -> Vec<&'static str> {
    match ns {
        NS_ENTITIES => ENTITIES.iter().map(|e| e.name).collect(),
        NS_ITEMS => ITEM_NAMES.to_vec(),
        NS_GROUNDS => GROUND_NAMES.to_vec(),
        NS_UNLOCKS => UNLOCKS.iter().map(|u| u.name).collect(),
        NS_HATS => HAT_NAMES.to_vec(),
        _ => LEADERBOARD_NAMES.to_vec(),
    }
}

fn entity_so(name: &str) -> &'static EntSO {
    ENTITIES.iter().find(|e| e.name == name).unwrap_or_else(|| panic!("unknown entity {name}"))
}
fn unlock_so(name: &str) -> Option<&'static UnlockSO> {
    UNLOCKS.iter().find(|u| u.name == name)
}
fn item_id(name: &str) -> usize {
    ITEM_NAMES.iter().position(|n| *n == name).unwrap_or_else(|| panic!("unknown item {name}"))
}

struct PyFunc {
    name: Rc<str>,
    syntax_tree: Option<Rc<Node>>,
    parent_scope: Option<ScopeRef>,
    binding: Option<&'static str>,
    method_object: Option<V>,
    is_free: bool,
}

struct PyModule {
    /// the module's global scope; its vars are the module's `elements`
    scope: ScopeRef,
    name: String,
    fully_initialized: Cell<bool>,
}

struct DroneHandle {
    id: i32,
    generation: i32,
    return_value: RefCell<Option<V>>,
}

#[derive(Clone)]
enum V {
    None,
    Num(f64),
    Bool(bool),
    Str(Rc<str>),
    List(Rc<RefCell<Vec<V>>>),
    Tuple(Rc<Vec<V>>),
    Dict(Rc<RefCell<DMap>>),
    Set(Rc<RefCell<DMap>>),
    Range(f64, f64, f64),
    Func(Rc<PyFunc>),
    Module(Rc<PyModule>),
    Bag(u8),
    Const(u8, &'static str),
    Dir(u8),
    Handle(Rc<DroneHandle>),
    Unassigned,
    /// InternalPySequence (argument lists, statement blocks, index lists)
    Seq(Rc<Vec<V>>),
}

/// What C# Dictionary/HashSet use to decide that two keys are the same key.
#[derive(Clone, PartialEq, Eq, Hash)]
enum Key {
    None,
    Num(u64),
    Str(Rc<str>),
    Tuple(Vec<Key>),
    Range(i64, u64, u64),
    Const(u8, &'static str),
    Bag(u8),
    Dir(u8),
    Handle(i32),
    Ref(usize),
}

/// Dictionary<IPyObject, PyObjectBox> / HashSet<IPyObject>: entries live in slots, removed slots go
/// on a LIFO free list and are reused by the next insert, and iteration walks the slots in order.
struct DMap {
    slots: Vec<Option<(V, V)>>,
    free: Vec<usize>,
    index: FxMap<Key, usize>,
    version: u64,
    is_set: bool,
}

impl DMap {
    fn new(is_set: bool) -> DMap {
        DMap { slots: Vec::new(), free: Vec::new(), index: FxMap::default(), version: 0, is_set }
    }
    fn len(&self) -> usize {
        self.index.len()
    }
    fn contains(&self, k: &Key) -> bool {
        self.index.contains_key(k)
    }
    fn get(&self, k: &Key) -> Option<V> {
        self.index.get(k).map(|i| self.slots[*i].as_ref().unwrap().1.clone())
    }
    /// dict[key] = value for a key that is not present yet / HashSet.Add
    fn insert_new(&mut self, key: Key, k: V, v: V) {
        let i = match self.free.pop() {
            Some(i) => {
                self.slots[i] = Some((k, v));
                i
            }
            None => {
                self.slots.push(Some((k, v)));
                self.slots.len() - 1
            }
        };
        self.index.insert(key, i);
        self.version += 1;
    }
    /// existing PyObjectBox.obj = value (does not count as a modification of the collection)
    fn set_existing(&mut self, key: &Key, v: V) {
        let i = self.index[key];
        self.slots[i].as_mut().unwrap().1 = v;
    }
    fn put(&mut self, key: Key, k: V, v: V) {
        if self.index.contains_key(&key) {
            self.set_existing(&key, v);
        } else {
            self.insert_new(key, k, v);
        }
    }
    fn remove(&mut self, key: &Key) -> Option<V> {
        let i = self.index.remove(key)?;
        let e = self.slots[i].take();
        self.version += 1;
        if self.is_set && self.index.is_empty() {
            self.slots.clear();
            self.free.clear();
        } else {
            self.free.push(i);
        }
        e.map(|e| e.1)
    }
    fn keys(&self) -> Vec<V> {
        self.slots.iter().flatten().map(|e| e.0.clone()).collect()
    }
    fn entries(&self) -> Vec<(V, V)> {
        self.slots.iter().flatten().cloned().collect()
    }
}

fn new_list(v: Vec<V>) -> V {
    V::List(Rc::new(RefCell::new(v)))
}
fn new_str(s: &str) -> V {
    V::Str(Rc::from(s))
}
fn tuple2(a: f64, b: f64) -> V {
    V::Tuple(Rc::new(vec![V::Num(a), V::Num(b)]))
}

impl V {
    /// `is PyNumber` (PyBool derives from PyNumber)
    fn num(&self) -> Option<f64> {
        match self {
            V::Num(n) => Some(*n),
            V::Bool(b) => Some(if *b { 1.0 } else { 0.0 }),
            _ => None,
        }
    }
    fn is_none(&self) -> bool {
        matches!(self, V::None)
    }
    /// `is IPySequence`
    fn is_seq(&self) -> bool {
        matches!(self, V::Str(_) | V::List(_) | V::Tuple(_) | V::Range(..) | V::Seq(_))
    }
    /// PyDict, PyList, PySet or PyModule: the types that cannot be dictionary keys
    fn is_unhashable(&self) -> bool {
        matches!(self, V::Dict(_) | V::List(_) | V::Set(_) | V::Module(_))
    }
    fn ptr(&self) -> usize {
        match self {
            V::List(r) => Rc::as_ptr(r) as *const u8 as usize,
            V::Tuple(r) => Rc::as_ptr(r) as *const u8 as usize,
            V::Dict(r) | V::Set(r) => Rc::as_ptr(r) as *const u8 as usize,
            V::Func(r) => Rc::as_ptr(r) as *const u8 as usize,
            V::Module(r) => Rc::as_ptr(r) as *const u8 as usize,
            V::Seq(r) => Rc::as_ptr(r) as *const u8 as usize,
            _ => 0,
        }
    }
}

fn range_count(start: f64, end: f64, step: f64) -> usize {
    ((end - start) / step).max(0.0).ceil() as i32 as usize
}

fn seq_len(v: &V) -> usize {
    match v {
        V::Str(s) => s.chars().count(),
        V::List(l) => l.borrow().len(),
        V::Tuple(t) | V::Seq(t) => t.len(),
        V::Range(s, e, st) => range_count(*s, *e, *st),
        _ => 0,
    }
}
fn seq_get(v: &V, i: usize) -> V {
    match v {
        V::Str(s) => V::Str(Rc::from(s.chars().nth(i).unwrap().to_string().as_str())),
        V::List(l) => l.borrow()[i].clone(),
        V::Tuple(t) | V::Seq(t) => t[i].clone(),
        V::Range(s, _, st) => V::Num(*s + i as f64 * *st),
        _ => V::None,
    }
}
fn seq_items(v: &V) -> Vec<V> {
    match v {
        V::List(l) => l.borrow().clone(),
        V::Tuple(t) | V::Seq(t) => t.to_vec(),
        _ => (0..seq_len(v)).map(|i| seq_get(v, i)).collect(),
    }
}

fn to_upper_snake(a: &str) -> String {
    let mut out = String::new();
    let mut prev = '_';
    for (i, c) in a.chars().enumerate() {
        if i == 0 || prev == '_' {
            out.extend(c.to_uppercase());
        } else {
            out.push(c);
        }
        prev = c;
    }
    out
}

/// double.ToString("0.##", InvariantCulture)
fn fmt_num(x: f64) -> String {
    if x.is_nan() {
        return "NaN".into();
    }
    if x.is_infinite() {
        return if x > 0.0 { "Infinity".into() } else { "-Infinity".into() };
    }
    let mut s = format!("{:.2}", (x * 100.0).round() / 100.0);
    while s.ends_with('0') {
        s.pop();
    }
    if s.ends_with('.') {
        s.pop();
    }
    if s == "-0" {
        s = "0".into();
    }
    s
}
/// double.ToString()
fn fmt_double(x: f64) -> String {
    if x == x.trunc() && x.abs() < 1e15 {
        format!("{}", x as i64)
    } else {
        format!("{}", x)
    }
}

/// CodeUtilities.ToNiceString
fn to_nice_string(obj: &V, depth: i32, loop_detector: &mut Vec<usize>, is_sequence_element: bool) -> String {
    if depth > 100 {
        return String::new();
    }
    if obj.is_none() {
        return "None".into();
    }
    if obj.ptr() != 0 && loop_detector.contains(&obj.ptr()) {
        return "...".into();
    }
    fn close(mut s: String, open: char, close_c: char) -> String {
        if s.len() > 1 {
            s.pop();
        }
        s.push(close_c);
        let _ = open;
        s
    }
    match obj {
        V::List(l) => {
            loop_detector.push(obj.ptr());
            let mut s = String::from("[");
            let items = l.borrow().clone();
            for it in items.iter() {
                s += &to_nice_string(it, depth + 1, loop_detector, true);
                s.push(',');
            }
            close(s, '[', ']')
        }
        V::Dict(d) => {
            loop_detector.push(obj.ptr());
            let mut s = String::from("{");
            let entries = d.borrow().entries();
            for (k, v) in entries.iter() {
                s += &to_nice_string(k, depth + 1, loop_detector, true);
                s.push(':');
                s += &to_nice_string(v, depth + 1, loop_detector, true);
                s.push(',');
            }
            close(s, '{', '}')
        }
        V::Set(d) => {
            let mut s = String::from("{");
            let keys = d.borrow().keys();
            for k in keys.iter() {
                s += &to_nice_string(k, depth + 1, loop_detector, true);
                s.push(',');
            }
            close(s, '{', '}')
        }
        V::Tuple(t) => {
            let mut s = String::from("(");
            for it in t.iter() {
                s += &to_nice_string(it, depth + 1, loop_detector, true);
                s.push(',');
            }
            close(s, '(', ')')
        }
        V::Num(n) => fmt_num(*n),
        V::Str(s) if is_sequence_element => format!("'{}'", s),
        _ => to_string(obj),
    }
}
fn nice(obj: &V) -> String {
    to_nice_string(obj, 0, &mut Vec::new(), false)
}
/// what LocalizeAndFormat puts into error messages
fn nice_el(obj: &V) -> String {
    to_nice_string(obj, 0, &mut Vec::new(), true)
}

/// Convert.ToString(obj)
fn to_string(obj: &V) -> String {
    match obj {
        V::None => "None".into(),
        V::Num(n) => fmt_double(*n),
        V::Bool(b) => if *b { "True".into() } else { "False".into() },
        V::Str(s) => s.to_string(),
        V::Range(s, e, st) => {
            if *st == 1.0 {
                format!("range({},{})", fmt_double(*s), fmt_double(*e))
            } else {
                format!("range({},{},{})", fmt_double(*s), fmt_double(*e), fmt_double(*st))
            }
        }
        V::Func(f) => f.name.to_string(),
        V::Module(m) => format!("<Module {}>", m.name),
        V::Bag(ns) => NS_NAMES[*ns as usize].into(),
        V::Const(ns, name) => format!("{}.{}", NS_NAMES[*ns as usize], to_upper_snake(name)),
        V::Dir(d) => ["North", "East", "South", "West"][*d as usize].into(),
        V::Handle(h) => format!("<drone {}>", h.generation),
        V::Unassigned => "PyUnassigned".into(),
        _ => nice(obj),
    }
}

fn err(key: &str, args: &[String]) -> String {
    if args.is_empty() {
        key.to_string()
    } else {
        format!("{} [{}]", key, args.join(", "))
    }
}

/// CodeUtilities.AssertMaxComparisonDepth
fn assert_max_comparison_depth(steps: &mut i32) -> R<()> {
    if *steps > 1000 {
        return Err("error_max_comparison_depth".into());
    }
    if *steps >= 0 {
        *steps += 1;
    }
    Ok(())
}

/// IPySequence.PySequenceDeepEquals
fn seq_deep_equals(one: &V, two: &V, steps: &mut i32) -> R<bool> {
    let n = seq_len(one);
    if n != seq_len(two) {
        return Ok(false);
    }
    for i in 0..n {
        if !py_equals(&seq_get(one, i), &seq_get(two, i), steps)? {
            return Ok(false);
        }
    }
    Ok(true)
}

/// IPyObject.PyEquals, dispatched on the type of `a` like the C# virtual call
fn py_equals(a: &V, b: &V, steps: &mut i32) -> R<bool> {
    assert_max_comparison_depth(steps)?;
    Ok(match a {
        V::None => b.is_none(),
        V::Num(_) | V::Bool(_) => match b.num() {
            Some(y) => a.num().unwrap() == y,
            None => false,
        },
        V::Str(x) => match b {
            V::Str(y) => x == y,
            _ if b.is_seq() => seq_deep_equals(a, b, steps)?,
            _ => false,
        },
        V::List(_) | V::Seq(_) => {
            if b.is_seq() {
                seq_deep_equals(a, b, steps)?
            } else {
                false
            }
        }
        V::Tuple(_) => match b {
            V::Tuple(_) => seq_deep_equals(a, b, steps)?,
            _ => false,
        },
        V::Range(s, e, st) => match b {
            V::Range(s2, e2, st2) => {
                let c = range_count(*s, *e, *st);
                if range_count(*s2, *e2, *st2) != c {
                    false
                } else if c == 0 {
                    true
                } else {
                    *s2 == *s && *s2 + (c - 1) as f64 * *st2 == *s + (c - 1) as f64 * *st
                }
            }
            _ if b.is_seq() => seq_deep_equals(a, b, steps)?,
            _ => false,
        },
        V::Dict(d) => match b {
            V::Dict(d2) => {
                if d.borrow().len() != d2.borrow().len() {
                    false
                } else {
                    let entries = d.borrow().entries();
                    let mut same = true;
                    for (k, v) in entries.iter() {
                        let key = to_key(k)?;
                        let other = d2.borrow().get(&key);
                        match other {
                            None => {
                                same = false;
                                break;
                            }
                            Some(o) => {
                                if !py_equals(v, &o, steps)? {
                                    same = false;
                                    break;
                                }
                            }
                        }
                    }
                    same
                }
            }
            _ => false,
        },
        V::Set(d) => match b {
            V::Set(d2) => {
                if d.borrow().len() != d2.borrow().len() {
                    false
                } else {
                    let keys = d.borrow().keys();
                    let mut same = true;
                    for k in keys.iter() {
                        if !d2.borrow().contains(&to_key(k)?) {
                            same = false;
                            break;
                        }
                    }
                    same
                }
            }
            _ => false,
        },
        V::Func(f) => matches!(b, V::Func(g) if Rc::ptr_eq(f, g)),
        V::Module(m) => matches!(b, V::Module(n) if Rc::ptr_eq(m, n)),
        V::Bag(x) => matches!(b, V::Bag(y) if x == y),
        V::Const(ns, name) => matches!(b, V::Const(ns2, name2) if ns == ns2 && name == name2),
        V::Dir(x) => matches!(b, V::Dir(y) if x == y),
        V::Handle(h) => matches!(b, V::Handle(g) if g.generation == h.generation),
        V::Unassigned => false,
    })
}

/// GetHashCode + Equals as seen by Dictionary/HashSet
fn to_key(v: &V) -> R<Key> {
    Ok(match v {
        V::None | V::Unassigned => Key::None,
        V::Num(_) | V::Bool(_) => {
            let n = v.num().unwrap();
            Key::Num(if n == 0.0 { 0 } else { n.to_bits() })
        }
        V::Str(s) => Key::Str(s.clone()),
        V::Tuple(t) => {
            let mut ks = Vec::with_capacity(t.len());
            for e in t.iter() {
                if e.is_unhashable() {
                    return Err(err("error_bad_key", &[nice_el(v)]));
                }
                ks.push(to_key(e)?);
            }
            Key::Tuple(ks)
        }
        V::Range(s, e, st) => {
            let c = range_count(*s, *e, *st);
            if c == 0 {
                Key::Range(0, 0, 0)
            } else {
                Key::Range(c as i64, s.to_bits(), (*s + (c - 1) as f64 * *st).to_bits())
            }
        }
        V::Const(ns, name) => Key::Const(*ns, name),
        V::Bag(ns) => Key::Bag(*ns),
        V::Dir(d) => Key::Dir(*d),
        V::Handle(h) => Key::Handle(h.generation),
        _ => Key::Ref(v.ptr()),
    })
}

/// IPyObject.Size
fn py_size(v: &V) -> i32 {
    match v {
        V::Str(s) => (s.chars().count() as i32 / 8).max(1),
        V::List(l) => l.borrow().iter().map(py_size).sum(),
        V::Tuple(t) => t.iter().map(py_size).sum(),
        V::Dict(d) | V::Set(d) => d.borrow().keys().iter().map(py_size).sum(),
        V::Module(m) => m.scope.borrow().vars.len() as i32,
        _ => 1,
    }
}

/// CodeUtilities.DeepCompare
fn deep_compare(a: &V, b: &V, op: &str, steps: &mut i32) -> R<i32> {
    if a.is_none() && b.is_none() {
        return Ok(0);
    }
    if *steps > 1000 {
        return Err("error_max_comparison_depth".into());
    }
    *steps += 1;
    let bad = || err("error_bad_bin_operator", &[op.to_string(), nice_el(a), nice_el(b)]);
    if a.is_none() || b.is_none() {
        return Err(bad());
    }
    if let (Some(x), Some(y)) = (a.num(), b.num()) {
        return Ok(if x > y { 1 } else if x < y { -1 } else { 0 });
    }
    if let (V::Str(x), V::Str(y)) = (a, b) {
        return Ok(match x.as_ref().cmp(y.as_ref()) {
            std::cmp::Ordering::Less => -1,
            std::cmp::Ordering::Equal => 0,
            std::cmp::Ordering::Greater => 1,
        });
    }
    if a.is_seq() && b.is_seq() {
        let (n1, n2) = (seq_len(a), seq_len(b));
        let mut i = 0;
        while i < n1 && i < n2 {
            let (x, y) = (seq_get(a, i), seq_get(b, i));
            if !py_equals(&x, &y, steps)? {
                return deep_compare(&x, &y, op, steps);
            }
            i += 1;
        }
        return Ok(if n1 > n2 { 1 } else if n2 > n1 { -1 } else { 0 });
    }
    Err(bad())
}

/// Scope.IsTrueValue ("error forgot call" is enabled, as in the default options)
fn is_true_value(o: &V) -> R<bool> {
    Ok(match o {
        V::None => false,
        V::Num(_) | V::Bool(_) => o.num().unwrap() != 0.0,
        V::Str(_) | V::List(_) | V::Tuple(_) | V::Range(..) | V::Seq(_) => seq_len(o) > 0,
        V::Dict(d) | V::Set(d) => d.borrow().len() > 0,
        V::Bag(_) => true,
        V::Func(f) => return Err(err("error_function_as_condition", &[f.name.to_string()])),
        _ => true,
    })
}

/// IEnumerable<IPyObject>
fn is_enumerable(v: &V) -> bool {
    matches!(v, V::Str(_) | V::List(_) | V::Tuple(_) | V::Range(..) | V::Seq(_) | V::Dict(_) | V::Set(_) | V::Bag(_))
}
fn enumerate(v: &V) -> Vec<V> {
    match v {
        V::Dict(d) | V::Set(d) => d.borrow().keys(),
        V::Bag(ns) => ns_members(*ns).into_iter().map(|n| V::Const(*ns, n)).collect(),
        V::Range(s, e, st) => {
            let mut out = Vec::new();
            let mut it = PyIter::new(v);
            while let Ok(Some(x)) = it.next() {
                out.push(x);
            }
            out
        }
        _ => seq_items(v),
    }
}

/// The enumerators the `for` loop walks: lists by live index, ranges by repeated addition,
/// dicts and sets with the "collection was modified" check.
enum PyIter {
    Index(V, i64),
    Fixed(Vec<V>, usize),
    Range { i: f64, end: f64, step: f64 },
    Coll(Rc<RefCell<DMap>>, u64, usize),
}

impl PyIter {
    fn new(v: &V) -> PyIter {
        match v {
            V::List(_) | V::Tuple(_) | V::Seq(_) => PyIter::Index(v.clone(), -1),
            V::Range(s, e, st) => PyIter::Range { i: *s - *st, end: *e, step: *st },
            V::Dict(d) | V::Set(d) => PyIter::Coll(d.clone(), d.borrow().version, 0),
            _ => PyIter::Fixed(enumerate(v), 0),
        }
    }
    fn next(&mut self) -> R<Option<V>> {
        match self {
            PyIter::Index(v, i) => {
                *i += 1;
                Ok(if (*i as usize) < seq_len(v) { Some(seq_get(v, *i as usize)) } else { None })
            }
            PyIter::Fixed(items, i) => {
                *i += 1;
                Ok(items.get(*i - 1).cloned())
            }
            PyIter::Range { i, end, step } => {
                *i += *step;
                let more = if !(*step >= 0.0) { *end < *i } else { *i < *end };
                Ok(if more { Some(V::Num(*i)) } else { None })
            }
            PyIter::Coll(d, version, pos) => {
                let m = d.borrow();
                if m.version != *version {
                    return Err("error_collection_changed_size_during_iteration".into());
                }
                while *pos < m.slots.len() {
                    *pos += 1;
                    if let Some(e) = &m.slots[*pos - 1] {
                        return Ok(Some(e.0.clone()));
                    }
                }
                Ok(None)
            }
        }
    }
}

/// PyNumber.Modulo / FloorDivision
fn py_modulo(lhs: f64, rhs: f64) -> f64 {
    let num = lhs % rhs;
    if num * rhs < 0.0 { num + rhs } else { num }
}

/// IPyIndexable.At for sequences and PyDict.At
fn index_at(target: &V, indices: &[V], steps: &mut i32, value_to_set: Option<V>) -> R<V> {
    if let V::Dict(d) = target {
        if indices.len() != 1 {
            return Err("error_slice_dict".into());
        }
        let k = &indices[0];
        if k.is_unhashable() {
            return Err(err("error_bad_key", &[nice_el(k)]));
        }
        let key = to_key(k)?;
        if !d.borrow().contains(&key) && value_to_set.is_none() {
            return Err(err("error_key", &[nice_el(k)]));
        }
        *steps = py_size(k).max(1);
        if let Some(v) = value_to_set {
            d.borrow_mut().put(key.clone(), k.clone(), v);
        }
        return Ok(d.borrow().get(&key).unwrap());
    }
    let count = seq_len(target) as f64;
    let all_num_or_none = indices.iter().all(|o| o.num().is_some() || o.is_none());
    if !all_num_or_none && (indices.len() < 3 || !indices[2].is_none()) {
        return Err(err("error_index", &[nice_el(&indices[0]), nice_el(target)]));
    }
    let index_from = |o: &V, is_start: bool| -> R<f64> {
        let mut num = match o.num() {
            Some(n) => n,
            None => {
                if !o.is_none() {
                    return Err(err("error_index", &[nice_el(o), nice_el(target)]));
                }
                let neg_step = indices.len() == 3 && (indices[2].num().unwrap_or(1.0) as i32) < 0;
                if neg_step == is_start { count } else { -1.0 }
            }
        };
        if num < 0.0 && !o.is_none() {
            num += count;
        }
        Ok(num)
    };
    let mut num = index_from(&indices[0], true)?;
    if indices.len() == 1 {
        if indices[0].is_none() {
            return Err(err("error_index", &[nice_el(&indices[0]), nice_el(target)]));
        }
        if num < 0.0 || num >= count || num.is_nan() {
            return Err(err("error_index_out_of_bounds", &[fmt_num(num), nice_el(target)]));
        }
        *steps = 1;
        if let Some(v) = value_to_set {
            match target {
                V::List(l) => l.borrow_mut()[num as i32 as usize] = v,
                V::Tuple(_) => return Err("error_index_on_tuple".into()),
                _ => return Err(err("error_index", &[nice_el(&indices[0]), nice_el(target)])),
            }
        }
        return Ok(seq_get(target, num as i32 as usize));
    }
    let mut val = index_from(&indices[1], false)?;
    let step = if indices.len() == 3 {
        indices[2].num().ok_or_else(|| "error_index".to_string())?
    } else {
        1.0
    };
    if step == 0.0 {
        return Err("error_zero_step".into());
    }
    if step > 0.0 {
        num = num.max(0.0);
        val = val.min(count);
    } else {
        val = val.max(-1.0);
        num = num.min(count - 1.0);
    }
    let mut out = Vec::new();
    let mut i = num;
    while i >= 0.0 && i < count && ((step >= 0.0 && i < val) || (step < 0.0 && i > val)) {
        out.push(seq_get(target, i as i32 as usize));
        i += step;
    }
    *steps = (out.len() as i32).max(1);
    Ok(match target {
        V::Tuple(_) => V::Tuple(Rc::new(out)),
        V::Str(_) => new_str(&out.iter().map(to_string).collect::<String>()),
        _ => new_list(out),
    })
}

/// PyContains on a sequence
fn seq_contains(container: &V, obj: &V, steps: &mut i32) -> R<bool> {
    match container {
        V::Str(s) => {
            *steps += s.chars().count() as i32;
            match obj {
                V::Str(o) => Ok(s.contains(o.as_ref())),
                _ => Err(err("error_in_string", &[nice_el(obj)])),
            }
        }
        V::Range(start, end, step) => {
            *steps += 8;
            let num = match obj.num() {
                Some(n) => n,
                None => return Ok(false),
            };
            Ok(if *step > 0.0 {
                num >= *start && num < *end && (num - *start) % *step == 0.0
            } else {
                num <= *start && num > *end && (*start - num) % *step == 0.0
            })
        }
        _ => {
            for el in seq_items(container).iter() {
                if py_equals(obj, el, steps)? {
                    return Ok(true);
                }
            }
            Ok(false)
        }
    }
}

// DeepCopy (spawn_drone and wait_for copy everything that crosses between drones)
struct Copies {
    values: FxMap<usize, V>,
    scopes: FxMap<usize, ScopeRef>,
    filled: HashSet<usize, FxBuild>,
}

impl Copies {
    fn new() -> Copies {
        Copies { values: FxMap::default(), scopes: FxMap::default(), filled: HashSet::default() }
    }
}

fn deep_copy(v: &V, copies: &mut Copies) -> V {
    let p = v.ptr();
    match v {
        V::List(l) => {
            if let Some(c) = copies.values.get(&p) {
                return c.clone();
            }
            let out = Rc::new(RefCell::new(Vec::new()));
            copies.values.insert(p, V::List(out.clone()));
            let items = l.borrow().clone();
            for it in items.iter() {
                let c = deep_copy(it, copies);
                out.borrow_mut().push(c);
            }
            V::List(out)
        }
        V::Tuple(t) => {
            if let Some(c) = copies.values.get(&p) {
                return c.clone();
            }
            let out = V::Tuple(Rc::new(t.iter().map(|e| deep_copy(e, copies)).collect()));
            copies.values.insert(p, out.clone());
            out
        }
        V::Dict(d) | V::Set(d) => {
            if let Some(c) = copies.values.get(&p) {
                return c.clone();
            }
            let is_set = d.borrow().is_set;
            let out = Rc::new(RefCell::new(DMap::new(is_set)));
            let res = if is_set { V::Set(out.clone()) } else { V::Dict(out.clone()) };
            copies.values.insert(p, res.clone());
            let entries = d.borrow().entries();
            for (k, val) in entries.iter() {
                let k2 = deep_copy(k, copies);
                let v2 = deep_copy(val, copies);
                if let Ok(key) = to_key(&k2) {
                    out.borrow_mut().put(key, k2, v2);
                }
            }
            res
        }
        V::Func(f) => {
            if let Some(c) = copies.values.get(&p) {
                return c.clone();
            }
            // The copy is registered before its parent scope is filled in, like `copies[this] = new PyFunction`.
            let parent = f.parent_scope.as_ref().map(|s| scope_shell(s, copies));
            let method_object = f.method_object.as_ref().map(|m| deep_copy(m, copies));
            let out = V::Func(Rc::new(PyFunc {
                name: f.name.clone(),
                syntax_tree: f.syntax_tree.clone(),
                parent_scope: parent,
                binding: f.binding,
                method_object,
                is_free: f.is_free,
            }));
            copies.values.insert(p, out.clone());
            if let Some(s) = &f.parent_scope {
                scope_deep_copy(s, copies);
            }
            out
        }
        V::Module(m) => {
            if let Some(c) = copies.values.get(&p) {
                return c.clone();
            }
            let scope = new_scope(None, None, &[]);
            let nm = Rc::new(PyModule {
                scope: scope.clone(),
                name: m.name.clone(),
                fully_initialized: Cell::new(m.fully_initialized.get()),
            });
            copies.values.insert(p, V::Module(nm.clone()));
            let entries = m.scope.borrow().vars.entries();
            for (k, val, st) in entries.iter() {
                let c = deep_copy(val, copies);
                scope.borrow_mut().vars.set(k, c, *st);
            }
            V::Module(nm)
        }
        _ => v.clone(),
    }
}

// ---- data decoded from the game's assets (EntitySO / UnlockSO) ----
struct EntSO { name: &'static str, class: &'static str, swappable: bool, placeable_on: &'static [&'static str], mean_grow: f32, grow_dev: f32, companion: bool, random_rotation: bool, can_be_planted: bool, overplant: bool, can_be_weird: bool, drop_item: &'static str, drop_amount: f64, yield_upgrade: &'static str, cost: &'static [(&'static str, f64)] }
static ENTITIES: &[EntSO] = &[
    EntSO { name: "apple", class: "Apple", swappable: false, placeable_on: &["soil", "grassland"], mean_grow: 0.2, grow_dev: 0.0, companion: false, random_rotation: true, can_be_planted: false, overplant: false, can_be_weird: true, drop_item: "", drop_amount: 0.0, yield_upgrade: "dinosaurs", cost: &[("cactus", 2.0)] },
    EntSO { name: "bamboo", class: "Bamboo", swappable: false, placeable_on: &["soil", "dirt", "perlite"], mean_grow: 1.0, grow_dev: 0.0, companion: false, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: false, drop_item: "bamboo", drop_amount: 1.0, yield_upgrade: "bamboo", cost: &[("rice", 1.0)] },
    EntSO { name: "bush", class: "BushPlant", swappable: false, placeable_on: &["grassland", "soil", "perlite"], mean_grow: 4.0, grow_dev: 0.2, companion: true, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "wood", drop_amount: 1.0, yield_upgrade: "trees", cost: &[] },
    EntSO { name: "cactus", class: "Cactus", swappable: true, placeable_on: &["soil", "perlite"], mean_grow: 1.0, grow_dev: 0.0, companion: false, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "cactus", drop_amount: 1.0, yield_upgrade: "cactus", cost: &[("pumpkin", 2.0)] },
    EntSO { name: "carrot", class: "Growable", swappable: false, placeable_on: &["soil", "loam"], mean_grow: 6.0, grow_dev: 0.2, companion: true, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "carrot", drop_amount: 1.0, yield_upgrade: "carrots", cost: &[("wood", 1.0), ("hay", 1.0)] },
    EntSO { name: "dead_pumpkin", class: "DeadPumpkin", swappable: false, placeable_on: &[], mean_grow: 0.0, grow_dev: 0.0, companion: false, random_rotation: true, can_be_planted: false, overplant: true, can_be_weird: true, drop_item: "", drop_amount: 0.0, yield_upgrade: "", cost: &[] },
    EntSO { name: "dinosaur", class: "Dinosaur", swappable: false, placeable_on: &["soil", "grassland"], mean_grow: 0.2, grow_dev: 0.1, companion: false, random_rotation: true, can_be_planted: false, overplant: false, can_be_weird: true, drop_item: "bone", drop_amount: 1.0, yield_upgrade: "dinosaurs", cost: &[] },
    EntSO { name: "dynamite", class: "Dynamite", swappable: false, placeable_on: &["all"], mean_grow: 0.0, grow_dev: 0.0, companion: false, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "dynamite", drop_amount: 1.0, yield_upgrade: "", cost: &[("dynamite", 1.0)] },
    EntSO { name: "grass", class: "Growable", swappable: false, placeable_on: &["soil", "grassland"], mean_grow: 0.5, grow_dev: 0.0, companion: true, random_rotation: true, can_be_planted: true, overplant: true, can_be_weird: true, drop_item: "hay", drop_amount: 1.0, yield_upgrade: "grass", cost: &[] },
    EntSO { name: "hedge", class: "HedgePlant", swappable: false, placeable_on: &["soil", "grassland"], mean_grow: 0.0, grow_dev: 0.0, companion: false, random_rotation: false, can_be_planted: false, overplant: false, can_be_weird: true, drop_item: "", drop_amount: 1.0, yield_upgrade: "mazes", cost: &[("weird_substance", 1.0)] },
    EntSO { name: "pumpkin", class: "Pumpkin", swappable: false, placeable_on: &["soil"], mean_grow: 2.0, grow_dev: 0.9, companion: false, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "pumpkin", drop_amount: 1.0, yield_upgrade: "pumpkins", cost: &[("carrot", 1.0)] },
    EntSO { name: "rice", class: "Rice", swappable: false, placeable_on: &["clay"], mean_grow: 6.0, grow_dev: 0.2, companion: false, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "rice", drop_amount: 1.0, yield_upgrade: "rice", cost: &[] },
    EntSO { name: "sunflower", class: "Sunflower", swappable: false, placeable_on: &["soil", "loam"], mean_grow: 7.0, grow_dev: 0.2, companion: false, random_rotation: false, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "power", drop_amount: 1.0, yield_upgrade: "", cost: &[("carrot", 1.0)] },
    EntSO { name: "treasure", class: "Treasure", swappable: false, placeable_on: &["soil", "grassland"], mean_grow: 0.0, grow_dev: 0.0, companion: false, random_rotation: false, can_be_planted: false, overplant: false, can_be_weird: true, drop_item: "gold", drop_amount: 1.0, yield_upgrade: "mazes", cost: &[("weird_substance", 1.0)] },
    EntSO { name: "tree", class: "TreePlant", swappable: false, placeable_on: &["soil", "grassland", "perlite"], mean_grow: 7.0, grow_dev: 0.2, companion: true, random_rotation: true, can_be_planted: true, overplant: false, can_be_weird: true, drop_item: "wood", drop_amount: 5.0, yield_upgrade: "trees", cost: &[] },
    EntSO { name: "underground_treasure", class: "UndergroundTreasure", swappable: false, placeable_on: &[], mean_grow: 0.0, grow_dev: 0.0, companion: false, random_rotation: false, can_be_planted: false, overplant: false, can_be_weird: true, drop_item: "gold", drop_amount: 1.0, yield_upgrade: "treasure_map", cost: &[] },
];
struct UnlockSO { name: &'static str, unlocks: &'static [&'static str], parent: &'static str, req: (&'static str, i32), cost: &'static [(&'static str, f64)], multi_cost: &'static [&'static [(&'static str, f64)]], multi_factor: f32, max_level: i32 }
static UNLOCKS: &[UnlockSO] = &[
    UnlockSO { name: "auto_unlock", unlocks: &["Unlocks", "unlock", "num_unlocked"], parent: "costs", req: ("", 0), cost: &[("pumpkin", 5000.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "bamboo", unlocks: &["bamboo", "measure", "hover", "get_hover"], parent: "rice", req: ("", 0), cost: &[("rice", 50.0)], multi_cost: &[&[("rice", 400.0)], &[("rice", 800.0)], &[("mushroom", 100.0)]], multi_factor: 4.0, max_level: 8 },
    UnlockSO { name: "cactus", unlocks: &["swap", "cactus_seed", "measure"], parent: "pumpkins", req: ("", 0), cost: &[("pumpkin", 5000.0)], multi_cost: &[&[("pumpkin", 20000.0)]], multi_factor: 6.0, max_level: 6 },
    UnlockSO { name: "carrots", unlocks: &["carrot", "till", "can_trade", "trade", "Items", "carrot_seed"], parent: "plant", req: ("", 0), cost: &[("wood", 50.0)], multi_cost: &[&[("wood", 250.0)]], multi_factor: 5.0, max_level: 10 },
    UnlockSO { name: "coal", unlocks: &[], parent: "mining", req: ("", 0), cost: &[("block", 20.0)], multi_cost: &[&[("rice", 150.0)], &[("rice", 1000.0)]], multi_factor: 4.0, max_level: 5 },
    UnlockSO { name: "costs", unlocks: &["get_cost", "Unlocks"], parent: "dictionaries", req: ("", 0), cost: &[("pumpkin", 2500.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "debug", unlocks: &["print", "quick_print", "Unlocks", "str", "output"], parent: "plant", req: ("", 0), cost: &[("hay", 50.0), ("wood", 50.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "debug_2", unlocks: &["set_execution_speed", "set_world_size", "debug2"], parent: "debug", req: ("", 0), cost: &[("gold", 500.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "debug_place", unlocks: &["place", "Grounds", "num_items", "None", "block_red", "block_green", "block_blue"], parent: "bamboo", req: ("", 0), cost: &[("bamboo", 1200.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "dictionaries", unlocks: &["dicts", "sets", "add", "dict", "set"], parent: "lists", req: ("", 0), cost: &[("pumpkin", 2500.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "dinosaurs", unlocks: &["dinosaur", "egg", "bone", "change_hat", "hats", "dinosaur_hat", "apple", "can_move"], parent: "cactus", req: ("", 0), cost: &[("cactus", 2000.0)], multi_cost: &[&[("cactus", 12000.0)]], multi_factor: 6.0, max_level: 6 },
    UnlockSO { name: "dynamite", unlocks: &["dynamite", "dynamite_ground", "soot"], parent: "mushrooms", req: ("expand", 4), cost: &[("mushroom", 80.0), ("gold", 4000.0)], multi_cost: &[&[("mushroom", 400.0)], &[("quartz", 50.0)]], multi_factor: 4.0, max_level: 5 },
    UnlockSO { name: "expand", unlocks: &["move", "North", "South", "East", "West", "expand_1", "2for", "2range", "2get_world_size", "2expand_2"], parent: "speed", req: ("", 0), cost: &[("hay", 30.0)], multi_cost: &[&[("wood", 20.0)], &[("wood", 30.0), ("carrot", 20.0)], &[("wood", 100.0), ("carrot", 50.0)], &[("pumpkin", 1000.0)]], multi_factor: 8.0, max_level: 9 },
    UnlockSO { name: "explosive_drill", unlocks: &["explosive_drill"], parent: "dynamite", req: ("", 0), cost: &[("dynamite", 12000000.0), ("mushroom", 120000.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "fertilizer", unlocks: &["use_item", "weird_substance"], parent: "watering", req: ("", 0), cost: &[("wood", 500.0)], multi_cost: &[&[("wood", 1500.0)]], multi_factor: 6.0, max_level: 4 },
    UnlockSO { name: "functions", unlocks: &["functions", "def", "return", "global", "tuples", "scopes"], parent: "variables", req: ("", 0), cost: &[("carrot", 40.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "grass", unlocks: &[], parent: "loops", req: ("", 0), cost: &[("hay", 100.0)], multi_cost: &[&[("hay", 300.0)], &[("wood", 500.0)]], multi_factor: 5.0, max_level: 10 },
    UnlockSO { name: "hats", unlocks: &["change_hat", "gray_hat", "purple_hat", "green_hat", "brown_hat"], parent: "loops", req: ("", 0), cost: &[("hay", 50.0)], multi_cost: &[&[]], multi_factor: 4.0, max_level: 1 },
    UnlockSO { name: "import", unlocks: &["from"], parent: "functions", req: ("", 0), cost: &[("carrot", 80.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "iron", unlocks: &[], parent: "coal", req: ("expand", 3), cost: &[("block", 90.0)], multi_cost: &[&[("coal", 50.0)], &[("coal", 150.0)], &[("coal", 450.0)], &[("bamboo", 10000000.0)]], multi_factor: 3.0, max_level: 5 },
    UnlockSO { name: "jump", unlocks: &["Unlocks"], parent: "coal", req: ("", 0), cost: &[("iron", 5.0), ("coal", 30.0)], multi_cost: &[], multi_factor: 4.0, max_level: 1 },
    UnlockSO { name: "leaderboard", unlocks: &["leaderboard_run", "Leaderboards"], parent: "simulation", req: ("", 0), cost: &[("gold", 1000000.0), ("bone", 2000000.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "lists", unlocks: &["append", "remove", "pop", "insert", "len", "list"], parent: "variables", req: ("", 0), cost: &[("carrot", 500.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "loops", unlocks: &["while", "True", "False", "break", "continue"], parent: "", req: ("", 0), cost: &[("hay", 5.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "mazes", unlocks: &["hedge", "treasure", "gold", "measure", "can_move"], parent: "fertilizer", req: ("", 0), cost: &[("weird_substance", 1000.0)], multi_cost: &[&[("cactus", 12000.0)]], multi_factor: 6.0, max_level: 6 },
    UnlockSO { name: "megafarm", unlocks: &["get_drone_id", "num_drones", "max_drones", "wait_for", "spawn_drone", "has_finished"], parent: "mazes", req: ("", 0), cost: &[("gold", 2000.0)], multi_cost: &[&[("gold", 8000.0)]], multi_factor: 4.0, max_level: 5 },
    UnlockSO { name: "mining", unlocks: &["dig", "dirt", "rock", "mining_hat", "block", "limestone"], parent: "expand", req: ("", 0), cost: &[("carrot", 20.0)], multi_cost: &[&[("block", 50.0)], &[("rice", 60.0)], &[("coal", 30.0)], &[("bamboo", 200.0)], &[("iron", 70.0)], &[("quartz", 90.0)], &[("mushroom", 250.0)]], multi_factor: 2.0, max_level: 8 },
    UnlockSO { name: "mushrooms", unlocks: &["push", "can_push", "mushroom", "measure", "place"], parent: "quartz", req: ("", 0), cost: &[("quartz", 60.0), ("pumpkin", 100.0)], multi_cost: &[&[("gold", 600.0)]], multi_factor: 5.0, max_level: 5 },
    UnlockSO { name: "operators", unlocks: &["and", "or", "not"], parent: "plant", req: ("", 0), cost: &[("hay", 150.0), ("wood", 10.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "ore_boost", unlocks: &[], parent: "quartz", req: ("expand", 3), cost: &[("coal", 200.0), ("iron", 100.0), ("quartz", 20.0)], multi_cost: &[], multi_factor: 3.0, max_level: 1 },
    UnlockSO { name: "petrified_pumpkins", unlocks: &["pumpkin", "petrified_pumpkin"], parent: "rice", req: ("expand", 3), cost: &[("rice", 50.0), ("iron", 5.0)], multi_cost: &[&[("bamboo", 1000.0), ("iron", 10.0)], &[("bamboo", 30000.0)]], multi_factor: 5.0, max_level: 7 },
    UnlockSO { name: "plant", unlocks: &["wood", "bush", "Entities", "clear"], parent: "speed", req: ("", 0), cost: &[("hay", 50.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "polyculture", unlocks: &["get_companion"], parent: "pumpkins", req: ("", 0), cost: &[("pumpkin", 3000.0)], multi_cost: &[&[("bone", 10000.0)]], multi_factor: 5.0, max_level: 5 },
    UnlockSO { name: "prospecting", unlocks: &["prospect_iron"], parent: "iron", req: ("", 0), cost: &[("coal", 32.0)], multi_cost: &[], multi_factor: 5.0, max_level: 1 },
    UnlockSO { name: "pumpkins", unlocks: &["pumpkin", "pumpkin_seed", "dead_pumpkin"], parent: "trees", req: ("", 0), cost: &[("wood", 500.0), ("carrot", 200.0)], multi_cost: &[&[("carrot", 1000.0)]], multi_factor: 4.0, max_level: 10 },
    UnlockSO { name: "pyramid", unlocks: &["limestone", "block", "place", "sand", "Grounds"], parent: "bamboo", req: ("expand", 4), cost: &[("bamboo", 10000.0)], multi_cost: &[&[("gold", 400.0)]], multi_factor: 4.0, max_level: 5 },
    UnlockSO { name: "quartz", unlocks: &["prospect_quartz"], parent: "iron", req: ("", 0), cost: &[("iron", 50.0)], multi_cost: &[&[("iron", 200.0)]], multi_factor: 2.0, max_level: 4 },
    UnlockSO { name: "rice", unlocks: &["clay", "dry_rice_terrace", "rice_terrace"], parent: "mining", req: ("expand", 2), cost: &[("coal", 10.0)], multi_cost: &[&[("block", 100.0)], &[("block", 500.0)], &[("block", 1000.0)]], multi_factor: 2.0, max_level: 8 },
    UnlockSO { name: "senses", unlocks: &["get_entity_type", "get_pos_x", "get_pos_y", "None", "num_items", "Items", "num_unlocked", "get_ground_type", "Grounds"], parent: "operators", req: ("", 0), cost: &[("hay", 100.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "simulation", unlocks: &["simulate"], parent: "timing", req: ("", 0), cost: &[("gold", 5000.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "special_soils", unlocks: &["loam", "perlite"], parent: "rice", req: ("", 0), cost: &[("rice", 800.0), ("bamboo", 1000.0)], multi_cost: &[], multi_factor: 4.0, max_level: 1 },
    UnlockSO { name: "speed", unlocks: &["can_harvest", "if", "else", "elif"], parent: "loops", req: ("", 0), cost: &[("hay", 20.0)], multi_cost: &[&[("wood", 20.0)], &[("wood", 50.0), ("carrot", 50.0)], &[("carrot", 500.0)]], multi_factor: 2.0, max_level: 5 },
    UnlockSO { name: "sunflowers", unlocks: &["sunflower_seed", "sunflower", "power", "get_active_power", "measure"], parent: "watering", req: ("", 0), cost: &[("carrot", 500.0)], multi_cost: &[], multi_factor: 0.0, max_level: 1 },
    UnlockSO { name: "the_farmers_remains", unlocks: &["change_hat"], parent: "dinosaurs", req: ("", 0), cost: &[("bone", 100000000.0)], multi_cost: &[&[]], multi_factor: 4.0, max_level: 1 },
    UnlockSO { name: "timing", unlocks: &["get_time", "get_tick_count"], parent: "debug", req: ("", 0), cost: &[("pumpkin", 1000.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "top_hat", unlocks: &["change_hat"], parent: "mazes", req: ("", 0), cost: &[("gold", 100000000.0), ("cactus", 1000000000.0), ("hay", 1000000000.0), ("carrot", 1000000000.0), ("wood", 10000000000.0)], multi_cost: &[&[]], multi_factor: 4.0, max_level: 1 },
    UnlockSO { name: "treasure_map", unlocks: &["treasure_map", "basalt", "treasure_path", "treasure_goal", "underground_treasure", "measure"], parent: "iron", req: ("expand", 3), cost: &[("bamboo", 40000.0)], multi_cost: &[&[("pumpkin", 200.0)], &[("quartz", 40.0)]], multi_factor: 4.0, max_level: 5 },
    UnlockSO { name: "trees", unlocks: &["tree"], parent: "carrots", req: ("", 0), cost: &[("wood", 50.0), ("carrot", 70.0)], multi_cost: &[&[("hay", 300.0)]], multi_factor: 4.0, max_level: 10 },
    UnlockSO { name: "underground_leaderboard", unlocks: &["leaderboard_run", "Leaderboards"], parent: "dynamite", req: ("simulation", 1), cost: &[("dynamite", 20000.0), ("bamboo", 200000.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "underground_senses", unlocks: &["get_ground_type", "Grounds", "get_pos_z", "get_hardness", "get_stability", "num_unlocked", "None"], parent: "mining", req: ("", 0), cost: &[("block", 50.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "utilities", unlocks: &["min", "max", "abs", "random"], parent: "functions", req: ("", 0), cost: &[("pumpkin", 1000.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "variables", unlocks: &[], parent: "operators", req: ("", 0), cost: &[("carrot", 35.0)], multi_cost: &[], multi_factor: 2.0, max_level: 1 },
    UnlockSO { name: "watering", unlocks: &["water", "use_item", "get_water"], parent: "carrots", req: ("", 0), cost: &[("wood", 50.0)], multi_cost: &[&[("wood", 200.0)]], multi_factor: 4.0, max_level: 9 },
];

// ---------------------------------------------------------------------------------------------
// Scope
// ---------------------------------------------------------------------------------------------
/// Dictionary<string, (IPyObject val, bool isStatic)> with insertion order kept
/// Scopes this small are searched name by name; a larger one also keeps a map.
const SMALL_VARS: usize = 8;

struct Vars {
    /// keyed by the interned name's address (see intern); empty while there are at most
    /// SMALL_VARS names
    map: FxMap<usize, usize>,
    /// one bit per name held (bloom_bit): a clear bit means the name is certainly not here
    bloom: u64,
    items: Vec<(Rc<str>, V, bool)>,
}

impl Vars {
    fn new() -> Vars {
        Vars { map: FxMap::default(), bloom: 0, items: Vec::new() }
    }
    fn len(&self) -> usize {
        self.items.len()
    }
    /// the slot of the name with this key
    #[inline]
    fn find(&self, key: usize) -> Option<usize> {
        if self.bloom & bloom_bit(key) == 0 {
            return None;
        }
        if self.items.len() <= SMALL_VARS {
            self.items.iter().position(|e| name_key(&e.0) == key)
        } else {
            self.map.get(&key).copied()
        }
    }
    #[inline]
    fn get(&self, name: &str) -> Option<&(Rc<str>, V, bool)> {
        self.find(name_key(name)).map(|i| &self.items[i])
    }
    #[inline]
    fn contains(&self, name: &str) -> bool {
        self.find(name_key(name)).is_some()
    }
    fn set(&mut self, name: &str, v: V, is_static: bool) {
        match self.find(name_key(name)) {
            Some(i) => {
                let it = &mut self.items[i];
                it.1 = v;
                it.2 = is_static;
            }
            None => self.push(intern(name), v, is_static),
        }
    }
    /// sets a name already interned (an Rc from the parser)
    fn set_interned(&mut self, name: &Rc<str>, v: V, is_static: bool) {
        match self.find(name_key(name)) {
            Some(i) => {
                let it = &mut self.items[i];
                it.1 = v;
                it.2 = is_static;
            }
            None => self.push(name.clone(), v, is_static),
        }
    }
    fn push(&mut self, k: Rc<str>, v: V, is_static: bool) {
        let key = name_key(&k);
        self.bloom |= bloom_bit(key);
        self.items.push((k, v, is_static));
        let n = self.items.len();
        if n == SMALL_VARS + 1 {
            for (i, e) in self.items.iter().enumerate() {
                self.map.insert(name_key(&e.0), i);
            }
        } else if n > SMALL_VARS + 1 {
            self.map.insert(key, n - 1);
        }
    }
    fn entries(&self) -> Vec<(Rc<str>, V, bool)> {
        self.items.clone()
    }
}

struct Scope {
    function_node: Option<Rc<Node>>,
    parent_scope: Option<ScopeRef>,
    vars: Vars,
}
type ScopeRef = Rc<RefCell<Scope>>;

fn new_scope(function_node: Option<Rc<Node>>, parent: Option<ScopeRef>, variable_names: &[Rc<str>]) -> ScopeRef {
    let mut vars = Vars::new();
    for n in variable_names {
        vars.set_interned(n, V::Unassigned, false);
    }
    Rc::new(RefCell::new(Scope { function_node, parent_scope: parent, vars }))
}

/// Scope.SetVar
fn scope_set_var(scope: &ScopeRef, name: &str, value: V, is_static: bool) {
    let parent = {
        let mut s = scope.borrow_mut();
        if s.vars.contains(name) || s.parent_scope.is_none() {
            s.vars.set(name, value, is_static);
            return;
        }
        s.parent_scope.clone().unwrap()
    };
    scope_set_var(&parent, name, value, is_static);
}

/// Scope.ImportVar
fn scope_import_var(scope: &ScopeRef, name: &str, value: V, mut is_static: bool) {
    let mut s = scope.borrow_mut();
    if let Some(e) = s.vars.get(name) {
        if !matches!(e.1, V::Unassigned) {
            is_static = false;
        }
    }
    s.vars.set(name, value, is_static);
}

/// Scope.Evaluate
fn scope_evaluate(scope: &ScopeRef, name: &str) -> R<(V, bool)> {
    scope_lookup(scope, name, None)
}

/// Scope.Evaluate, remembering in `cache` which scope up the chain held the name and at which
/// slot. Drones running the same function have scopes with the same names in the same order, so
/// the next lookup usually goes straight there: the scopes it passes must not hold the name (their
/// filter bit is clear) and the slot must hold this very name, or it falls back to the full search.
/// Either way the answer is the first scope up the chain that holds the name.
#[inline]
fn scope_lookup(scope: &ScopeRef, name: &str, cache: Option<&Cell<u64>>) -> R<(V, bool)> {
    let key = name_key(name);
    let bit = bloom_bit(key);
    if let Some(c) = cache {
        let c = c.get();
        if c != 0 {
            let hops = (c & 0xff) - 1;
            let idx = (c >> 8) as usize;
            let mut s: &Scope = unsafe { &*scope.as_ptr() };
            let mut ok = true;
            for _ in 0..hops {
                if s.vars.bloom & bit != 0 {
                    ok = false;
                    break;
                }
                match &s.parent_scope {
                    Some(p) => s = unsafe { &*p.as_ptr() },
                    None => {
                        ok = false;
                        break;
                    }
                }
            }
            if ok {
                if let Some(e) = s.vars.items.get(idx) {
                    if name_key(&e.0) == key {
                        if matches!(e.1, V::Unassigned) {
                            return Err(err("error_use_before_assign", &[name.to_string()]));
                        }
                        return Ok((e.1.clone(), e.2));
                    }
                }
            }
        }
    }
    let mut hops = 0u64;
    let mut s: &Scope = unsafe { &*scope.as_ptr() };
    loop {
        if s.vars.bloom & bit != 0 {
            if let Some(i) = s.vars.find(key) {
                if let Some(c) = cache {
                    c.set(((i as u64) << 8) | (hops + 1));
                }
                let e = &s.vars.items[i];
                if matches!(e.1, V::Unassigned) {
                    return Err(err("error_use_before_assign", &[name.to_string()]));
                }
                return Ok((e.1.clone(), e.2));
            }
        }
        match &s.parent_scope {
            Some(p) => s = unsafe { &*p.as_ptr() },
            None => return Err(err("error_name_not_defined", &[name.to_string()])),
        }
        hops += 1;
    }
}

#[allow(dead_code)]
fn scope_evaluate_uncached(scope: &ScopeRef, name: &str) -> R<(V, bool)> {
    // Nothing else holds a scope mutably while a name is looked up.
    let mut s: &Scope = unsafe { &*scope.as_ptr() };
    loop {
        if let Some(e) = s.vars.get(name) {
            if matches!(e.1, V::Unassigned) {
                return Err(err("error_use_before_assign", &[name.to_string()]));
            }
            return Ok((e.1.clone(), e.2));
        }
        match &s.parent_scope {
            Some(p) => s = unsafe { &*p.as_ptr() },
            None => return Err(err("error_name_not_defined", &[name.to_string()])),
        }
    }
}

fn scope_ptr(s: &ScopeRef) -> usize {
    Rc::as_ptr(s) as *const u8 as usize
}

/// The registered (possibly still empty) copy of a scope.
fn scope_shell(s: &ScopeRef, copies: &mut Copies) -> ScopeRef {
    let p = scope_ptr(s);
    if let Some(c) = copies.scopes.get(&p) {
        return c.clone();
    }
    let ns = Rc::new(RefCell::new(Scope {
        function_node: s.borrow().function_node.clone(),
        parent_scope: None,
        vars: Vars::new(),
    }));
    copies.scopes.insert(p, ns.clone());
    ns
}

/// Scope.DeepCopy
fn scope_deep_copy(s: &ScopeRef, copies: &mut Copies) -> ScopeRef {
    let ns = scope_shell(s, copies);
    if !copies.filled.insert(scope_ptr(s)) {
        return ns;
    }
    let parent = s.borrow().parent_scope.clone();
    if let Some(p) = parent {
        let np = scope_deep_copy(&p, copies);
        ns.borrow_mut().parent_scope = Some(np);
    }
    let entries = s.borrow().vars.entries();
    for (k, v, st) in entries.iter() {
        let c = deep_copy(v, copies);
        ns.borrow_mut().vars.set(k, c, *st);
    }
    ns
}

/// Scope.EvaluateConstant
fn evaluate_constant(s: &str) -> Option<V> {
    Some(match s {
        "True" => V::Bool(true),
        "False" => V::Bool(false),
        "None" => V::None,
        "Items" => V::Bag(NS_ITEMS),
        "Entities" => V::Bag(NS_ENTITIES),
        "Grounds" => V::Bag(NS_GROUNDS),
        "Unlocks" => V::Bag(NS_UNLOCKS),
        "Leaderboards" => V::Bag(NS_LEADERBOARDS),
        "Hats" => V::Bag(NS_HATS),
        "North" => V::Dir(0),
        "East" => V::Dir(1),
        "South" => V::Dir(2),
        "West" => V::Dir(3),
        _ => return None,
    })
}

/// PyConstBag.Evaluate
fn bag_evaluate(ns: u8, value: &str) -> R<V> {
    let lower = value.to_lowercase();
    match ns_members(ns).into_iter().find(|n| *n == lower) {
        Some(n) => Ok(V::Const(ns, n)),
        None => Err(err("error_invalid_const", &[format!("{}.{}", NS_NAMES[ns as usize], to_upper_snake(&lower))])),
    }
}

static ALL_KEY_WORDS: &[&str] = &[
    "def", "while", "for", "if", "else", "elif", "and", "or", "not", "True", "False", "None", "Entities", "Grounds",
    "Items", "Unlocks", "Leaderboards", "Hats", "North", "South", "West", "East", "pass", "break", "continue",
    "return", "global", "import", "from",
];

// ---------------------------------------------------------------------------------------------
// Tokenizer
// ---------------------------------------------------------------------------------------------
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum TT {
    NoToken, Ignore, Num, Identifier, Str, Def, BracketOpen, BracketClose, SquareBracketOpen, SquareBracketClose,
    CurlBraceOpen, CurlBraceClose, Comma, Colon, Dot, NewLine, Assign, If, Else, Elif, For, In, While, Or, And, Not,
    Compare, Add, Mult, Exp, Arrow, Union, Pass, Return, Break, Continue, Global, Import, From, Unknown,
}

#[derive(Clone)]
struct Token {
    ty: TT,
    value: String,
    start: usize,
}

static CONSTANT_TOKENS: &[(&str, bool, TT)] = &[
    ("if", true, TT::If), ("else", true, TT::Else), ("for", true, TT::For), ("or", true, TT::Or),
    ("and", true, TT::And), ("return", true, TT::Return), ("def", true, TT::Def), ("while", true, TT::While),
    ("elif", true, TT::Elif), ("break", true, TT::Break), ("continue", true, TT::Continue), ("pass", true, TT::Pass),
    ("**", false, TT::Exp), ("==", false, TT::Compare), ("=", false, TT::Assign), ("!=", false, TT::Compare),
    ("<=", false, TT::Compare), (">=", false, TT::Compare), ("<", false, TT::Compare), (">", false, TT::Compare),
    ("(", false, TT::BracketOpen), (")", false, TT::BracketClose), ("+=", false, TT::Assign), ("+", false, TT::Add),
    ("-=", false, TT::Assign), ("->", false, TT::Arrow), ("-", false, TT::Add), ("*=", false, TT::Assign),
    ("//=", false, TT::Assign), ("//", false, TT::Mult), ("/=", false, TT::Assign), ("%=", false, TT::Assign),
    ("*", false, TT::Mult), ("/", false, TT::Mult), ("%", false, TT::Mult), ("[", false, TT::SquareBracketOpen),
    ("]", false, TT::SquareBracketClose), ("{", false, TT::CurlBraceOpen), ("}", false, TT::CurlBraceClose),
    (",", false, TT::Comma), (":", false, TT::Colon), ("|", false, TT::Union), ("global", true, TT::Global),
    ("import", true, TT::Import), ("from", true, TT::From),
];

fn is_word(c: char) -> bool {
    c.is_alphanumeric() || c == '_'
}

struct TokenStream {
    tokens: VecDeque<Token>,
    last_string_index: usize,
}

impl TokenStream {
    fn current(&self) -> Option<&Token> {
        self.tokens.front()
    }
    fn cur_ty(&self) -> TT {
        self.tokens.front().map(|t| t.ty).unwrap_or(TT::NoToken)
    }
    fn look_ahead_ty(&self) -> TT {
        self.tokens.get(1).map(|t| t.ty).unwrap_or(TT::NoToken)
    }
    fn current_string_end_index(&self) -> usize {
        match self.current() {
            None => self.last_string_index,
            Some(t) => t.start + t.value.chars().count(),
        }
    }
    fn current_string_start_index(&self) -> usize {
        match self.current() {
            None => self.last_string_index,
            Some(t) => t.start,
        }
    }
    fn add(&mut self, t: Token) {
        self.last_string_index = t.start + t.value.chars().count();
        self.tokens.push_back(t);
    }
}

/// Tokenizer.Tokenize; the regex alternatives are matched by hand in the same order.
fn tokenize(code: &str) -> R<TokenStream> {
    let text: Vec<char> = code.replace('\u{0B}', "\n").chars().collect();
    let mut stream = TokenStream { tokens: VecDeque::new(), last_string_index: 0 };
    stream.add(Token { ty: TT::NewLine, value: "\n".into(), start: 0 });
    let n = text.len();
    let mut num = 0usize;
    let starts_with = |pos: usize, s: &str| -> bool {
        let cs: Vec<char> = s.chars().collect();
        pos + cs.len() <= n && text[pos..pos + cs.len()] == cs[..]
    };
    let boundary = |pos: usize| -> bool {
        // \b after a word character
        pos >= n || !is_word(text[pos])
    };
    'outer: while num < n {
        for (t, needs_boundary, ty) in CONSTANT_TOKENS.iter() {
            let len = t.chars().count();
            if !starts_with(num, t) {
                continue;
            }
            if *needs_boundary && num + len < n {
                let c = text[num + len];
                if c.is_alphanumeric() || c == '_' {
                    continue;
                }
            }
            stream.add(Token { ty: *ty, value: t.to_string(), start: num });
            num += len;
            continue 'outer;
        }
        let c = text[num];
        let mut m: Option<(TT, usize)> = None;
        // NUM: (\d*\.)?\d+\b
        {
            let mut i = num;
            while i < n && text[i].is_ascii_digit() {
                i += 1;
            }
            if i < n && text[i] == '.' {
                let mut j = i + 1;
                while j < n && text[j].is_ascii_digit() {
                    j += 1;
                }
                if j > i + 1 && boundary(j) {
                    m = Some((TT::Num, j - num));
                }
            }
            if m.is_none() && i > num && boundary(i) {
                m = Some((TT::Num, i - num));
            }
        }
        // IN: (?:in|not\s+in)\b
        if m.is_none() {
            if starts_with(num, "in") && boundary(num + 2) {
                m = Some((TT::In, 2));
            } else if starts_with(num, "not") {
                let mut i = num + 3;
                while i < n && text[i].is_whitespace() {
                    i += 1;
                }
                if i > num + 3 && starts_with(i, "in") && boundary(i + 2) {
                    m = Some((TT::In, i + 2 - num));
                }
            }
        }
        // NOT: not\b
        if m.is_none() && starts_with(num, "not") && boundary(num + 3) {
            m = Some((TT::Not, 3));
        }
        // IDENTIFIER: [a-zA-Z_]\w*
        if m.is_none() && (c.is_ascii_alphabetic() || c == '_') {
            let mut i = num + 1;
            while i < n && is_word(text[i]) {
                i += 1;
            }
            m = Some((TT::Identifier, i - num));
        }
        // STRING: (['"])(.*?)\1
        if m.is_none() && (c == '\'' || c == '"') {
            let mut i = num + 1;
            while i < n && text[i] != '\n' && text[i] != c {
                i += 1;
            }
            if i < n && text[i] == c {
                m = Some((TT::Str, i + 1 - num));
            }
        }
        // NEW_LINE: \n( |\t)*
        if m.is_none() && c == '\n' {
            let mut i = num + 1;
            while i < n && (text[i] == ' ' || text[i] == '\t') {
                i += 1;
            }
            m = Some((TT::NewLine, i - num));
        }
        // IGNORE: whitespace other than \n
        if m.is_none() && c.is_whitespace() {
            let mut i = num;
            while i < n && text[i].is_whitespace() && text[i] != '\n' {
                i += 1;
            }
            m = Some((TT::Ignore, i - num));
        }
        // IGNORE: #.*
        if m.is_none() && c == '#' {
            let mut i = num;
            while i < n && text[i] != '\n' {
                i += 1;
            }
            m = Some((TT::Ignore, i - num));
        }
        if m.is_none() && c == '.' {
            m = Some((TT::Dot, 1));
        }
        if m.is_none() {
            let mut i = num;
            while i < n && !text[i].is_whitespace() {
                i += 1;
            }
            m = Some((TT::Unknown, i - num));
        }
        let (ty, len) = m.unwrap();
        if ty == TT::Unknown {
            let line = text[..num].iter().filter(|c| **c == '\n').count() + 1;
            return Err(format!("line {}: error_unknown_token `{}`", line, text[num..num + len].iter().collect::<String>()));
        }
        if ty != TT::Ignore {
            stream.add(Token { ty, value: text[num..num + len].iter().collect(), start: num });
        }
        num += len;
    }
    while let Some(last) = stream.tokens.back() {
        if last.ty != TT::NewLine {
            break;
        }
        stream.tokens.pop_back();
        stream.last_string_index = match stream.tokens.back() {
            Some(l) => l.start + l.value.chars().count(),
            None => 0,
        };
    }
    Ok(stream)
}

// ---------------------------------------------------------------------------------------------
// Syntax tree
// ---------------------------------------------------------------------------------------------
/// A binary operator, decided from its text once at parse time.
#[derive(Clone, Copy, PartialEq)]
enum BOp {
    And, Or, Dot, Index, Add, Sub, Mul, Div, FloorDiv, Mod, Pow, Other,
}
impl BOp {
    fn of(op: &str) -> BOp {
        match op {
            "and" => BOp::And,
            "or" => BOp::Or,
            "." => BOp::Dot,
            "[]" => BOp::Index,
            "+" => BOp::Add,
            "-" => BOp::Sub,
            "*" => BOp::Mul,
            "/" => BOp::Div,
            "//" => BOp::FloorDiv,
            "%" => BOp::Mod,
            "**" => BOp::Pow,
            _ => BOp::Other,
        }
    }
}
/// A comparison operator, decided from its text once at parse time. `Other` is text the game
/// does not recognise (e.g. "not  in" with two spaces), which it treats as true.
#[derive(Clone, Copy, PartialEq)]
enum COp {
    Eq, Ne, Ge, Le, Gt, Lt, In, NotIn, Other,
}
impl COp {
    fn of(op: &str) -> COp {
        match op {
            "==" => COp::Eq,
            "!=" => COp::Ne,
            ">=" => COp::Ge,
            "<=" => COp::Le,
            ">" => COp::Gt,
            "<" => COp::Lt,
            "in" => COp::In,
            "not in" => COp::NotIn,
            _ => COp::Other,
        }
    }
}

#[derive(Clone)]
enum NK {
    Seq,
    Value(Rc<str>),
    Literal(V),
    Call,
    Binary(Rc<str>, TT, BOp),
    Unary(Rc<str>),
    Comparison(Vec<Rc<str>>, Vec<COp>),
    Branch(bool),
    /// slots: [iterable, body, pattern]
    For,
    Assignment(Rc<str>),
    Def(Rc<str>, bool),
    /// slots: [body, default values...]
    Function { params: Vec<Rc<str>>, name: Rc<str>, vars: Vec<Rc<str>> },
    Return,
    Pass,
    Break,
    Continue,
    Global,
    Import { module_names: Vec<Rc<str>>, unpack: bool, unpack_all: bool, vars_to_unpack: Vec<Rc<str>>, is_static: bool },
    List,
    Tuple,
    Dict,
    Set,
    Bracket,
}

struct Node {
    kind: NK,
    slots: Vec<Rc<Node>>,
    word_start: usize,
    word_end: usize,
    file: Rc<FileInfo>,
    /// for a Value node: where its name was found last time, as (slot index << 8) | (scopes up + 1),
    /// 0 for not yet; see scope_lookup
    lookup: Cell<u64>,
}

struct FileInfo {
    name: String,
    line_starts: Vec<usize>,
}

impl FileInfo {
    fn line_of(&self, pos: usize) -> usize {
        match self.line_starts.binary_search(&pos) {
            Ok(i) => i + 1,
            Err(i) => i,
        }
    }
}

/// Parser-side node: owned so the parser can rotate operator chains the way the C# does.
struct PN {
    kind: NK,
    slots: Vec<PN>,
    start: usize,
    end: usize,
}

impl PN {
    fn new(kind: NK, start: usize, end: usize) -> PN {
        PN { kind, slots: Vec::new(), start, end }
    }
    fn with(kind: NK, start: usize, end: usize, slots: Vec<PN>) -> PN {
        PN { kind, slots, start, end }
    }
    fn into_node(self, file: &Rc<FileInfo>) -> Rc<Node> {
        Rc::new(Node {
            kind: self.kind,
            slots: self.slots.into_iter().map(|s| s.into_node(file)).collect(),
            word_start: self.start,
            word_end: self.end,
            file: file.clone(),
            lookup: Cell::new(0),
        })
    }
}

type SetRef = Rc<RefCell<HashSet<String>>>;
fn new_set() -> SetRef {
    Rc::new(RefCell::new(HashSet::new()))
}

struct Parser {
    stream: TokenStream,
    file: Rc<FileInfo>,
}

static OPERATORS: &[(&[TT], u8)] = &[
    (&[TT::Or], 0),
    (&[TT::And], 0),
    (&[TT::Not], 1),
    (&[TT::Compare, TT::In], 0),
    (&[TT::Add], 0),
    (&[TT::Mult], 0),
    (&[TT::Add], 1),
    (&[TT::Exp], 0),
    (&[TT::BracketOpen, TT::SquareBracketOpen, TT::Dot], 2),
];

impl Parser {
    fn perr<T>(&self, msg: &str, start: usize) -> R<T> {
        Err(format!("{}.py line {}: {}", self.file.name, self.file.line_of(start), msg))
    }
    fn cur(&self) -> TT {
        self.stream.cur_ty()
    }
    fn consume_any(&mut self) -> R<Token> {
        match self.stream.tokens.pop_front() {
            Some(t) => Ok(t),
            None => self.perr("error_unexpected_token", self.stream.last_string_index),
        }
    }
    /// TokenStream.Consume
    fn consume(&mut self, ty: TT, error: Option<&str>) -> R<Token> {
        let (cur_ty, start) = match self.stream.current() {
            None => {
                return self.perr(
                    error.unwrap_or(&format!("error_unexpected_token (expected {:?})", ty)),
                    self.stream.last_string_index,
                )
            }
            Some(t) => (t.ty, t.start),
        };
        if ty != TT::NoToken && cur_ty != ty {
            return self.perr(error.unwrap_or(&format!("error_unexpected_token (expected {:?})", ty)), start);
        }
        Ok(self.stream.tokens.pop_front().unwrap())
    }

    /// Parser.Parse
    fn parse(mut self) -> R<Rc<Node>> {
        let all_vars = new_set();
        let imported = new_set();
        let hash_set = new_set();
        let tree = self.block(-1, &hash_set, &hash_set, &all_vars, &imported, true, true)?;
        if self.stream.current().is_some() {
            return self.perr("error_code_after_block", self.stream.current_string_start_index());
        }
        let file = self.file.clone();
        Ok(tree.into_node(&file))
    }

    fn function(&mut self, indentation: i32, all_vars: &SetRef, imported: &SetRef, global: bool, is_static: bool) -> R<PN> {
        let token = self.consume(TT::Def, None)?;
        let token2 = self.consume(TT::Identifier, None)?;
        self.optional_generic_type_annotation()?;
        self.consume(TT::BracketOpen, None)?;
        self.line_breaks();
        let hash_set = new_set();
        let mut list: Vec<Rc<str>> = Vec::new();
        let mut list2: Vec<PN> = Vec::new();
        let mut flag = false;
        loop {
            if self.cur() == TT::BracketClose {
                break;
            }
            let value = self.consume(TT::Identifier, None)?.value;
            list.push(intern(value.as_str()));
            hash_set.borrow_mut().insert(value.clone());
            all_vars.borrow_mut().insert(value);
            self.optional_variable_type_annotation()?;
            self.line_breaks();
            if self.cur() == TT::Assign {
                self.consume(TT::Assign, None)?;
                self.line_breaks();
                list2.push(self.expression(0, true, TT::NoToken, false)?);
                flag = true;
            } else if flag {
                return self.perr("error_missing_default_parameter", token.start);
            }
            if self.cur() != TT::Comma {
                break;
            }
            self.consume(TT::Comma, None)?;
            self.line_breaks();
        }
        self.consume(TT::BracketClose, None)?;
        self.optional_return_type_annotation()?;
        let token3 = self.consume_colon()?;
        let body = self.block(indentation, &hash_set, &new_set(), all_vars, imported, false, true)?;
        let mut vars: Vec<Rc<str>> = hash_set.borrow().iter().map(|s| intern(s.as_str())).collect();
        vars.sort();
        let name: Rc<str> = intern(token2.value.as_str());
        let mut function_node = PN::new(
            NK::Function { params: list, name: name.clone(), vars },
            token.start,
            token3.start + token3.value.chars().count(),
        );
        function_node.slots.push(body);
        for item in list2 {
            function_node.slots.push(item);
        }
        Ok(PN::with(NK::Def(name, is_static), token.start, token.start + token.value.len(), vec![function_node]))
    }

    fn block(&mut self, prev_indentation: i32, vars: &SetRef, global_vars: &SetRef, all_vars: &SetRef, imported: &SetRef, global: bool, is_static: bool) -> R<PN> {
        if global && self.stream.current().is_none() {
            return Ok(PN::new(NK::Seq, 0, 0));
        }
        if self.cur() != TT::NewLine {
            return self.perr("error_no_statements", self.stream.current_string_start_index());
        }
        let mut start_index = self.stream.current_string_start_index() + 1;
        let indentation = self.get_indentation()?;
        if indentation <= prev_indentation {
            return self.perr("error_not_enough_indentation", start_index);
        }
        let mut list = Vec::new();
        let mut num = indentation;
        while num == indentation {
            self.consume(TT::NewLine, None)?;
            list.push(self.statement(indentation, vars, global_vars, all_vars, imported, global, is_static)?);
            if self.cur() != TT::NewLine {
                break;
            }
            num = self.get_indentation()?;
        }
        start_index = self.stream.current_string_start_index() + 1;
        if num > indentation {
            return self.perr("error_too_much_indentation", start_index);
        }
        if !global && list.is_empty() {
            return self.perr("error_no_statements", start_index);
        }
        Ok(PN::with(NK::Seq, 0, 0, list))
    }

    fn statement(&mut self, indentation: i32, vars: &SetRef, global_vars: &SetRef, all_vars: &SetRef, imported: &SetRef, global: bool, is_static: bool) -> R<PN> {
        let add_var = |name: &str| {
            if !global_vars.borrow().contains(name) {
                vars.borrow_mut().insert(name.to_string());
            }
            all_vars.borrow_mut().insert(name.to_string());
        };
        match self.cur() {
            TT::Def => {
                let def_node = self.function(indentation, all_vars, imported, global, is_static)?;
                if let NK::Def(name, _) = &def_node.kind {
                    add_var(name);
                }
                return Ok(def_node);
            }
            TT::Pass => {
                let t = self.consume(TT::Pass, None)?;
                return Ok(PN::new(NK::Pass, t.start, t.start + t.value.len()));
            }
            TT::Break => {
                let t = self.consume(TT::Break, None)?;
                return Ok(PN::new(NK::Break, t.start, t.start + t.value.len()));
            }
            TT::Continue => {
                let t = self.consume(TT::Continue, None)?;
                return Ok(PN::new(NK::Continue, t.start, t.start + t.value.len()));
            }
            TT::Return => {
                let t = self.consume(TT::Return, None)?;
                let mut node = PN::new(NK::Return, t.start, t.start + t.value.len());
                if self.stream.current().is_some() && self.cur() != TT::NewLine {
                    node.slots.push(self.tuple_or_expression(false, TT::BracketClose, None, false)?);
                }
                return Ok(node);
            }
            TT::Global => {
                self.consume(TT::Global, None)?;
                let t = self.consume(TT::Identifier, None)?;
                self.optional_variable_type_annotation()?;
                if vars.borrow().contains(&t.value) {
                    return self.perr(&err("error_assign_before_global", &[t.value.clone()]), t.start);
                }
                global_vars.borrow_mut().insert(t.value.clone());
                return Ok(PN::new(NK::Global, t.start, t.start + t.value.len()));
            }
            TT::Import => {
                let t = self.consume(TT::Import, None)?;
                let list = self.sequence_of_identifiers(Some("error_invalid_import"))?;
                for item in list.iter() {
                    add_var(item);
                }
                let end = self.stream.current_string_start_index().saturating_sub(1);
                return Ok(PN::new(
                    NK::Import {
                        module_names: list.iter().map(|s| intern(s.as_str())).collect(),
                        unpack: false,
                        unpack_all: false,
                        vars_to_unpack: Vec::new(),
                        is_static,
                    },
                    t.start,
                    end,
                ));
            }
            TT::From => {
                let t = self.consume(TT::From, None)?;
                let t8 = self.consume(TT::Identifier, Some("error_invalid_import"))?;
                self.consume(TT::Import, Some("error_invalid_import"))?;
                let module: Rc<str> = intern(t8.value.as_str());
                if self.stream.current().map(|c| c.value == "*").unwrap_or(false) {
                    if !global {
                        return self.perr("error_wildcard_imports_not_allowed_in_function", self.stream.current_string_start_index());
                    }
                    self.consume(TT::Mult, None)?;
                    imported.borrow_mut().insert(t8.value.clone());
                    return Ok(PN::new(
                        NK::Import { module_names: vec![module], unpack: true, unpack_all: true, vars_to_unpack: Vec::new(), is_static },
                        t.start,
                        self.stream.current_string_start_index(),
                    ));
                }
                let list2 = self.sequence_of_identifiers(None)?;
                for item in list2.iter() {
                    add_var(item);
                }
                return Ok(PN::new(
                    NK::Import {
                        module_names: vec![module],
                        unpack: true,
                        unpack_all: false,
                        vars_to_unpack: list2.iter().map(|s| intern(s.as_str())).collect(),
                        is_static,
                    },
                    t.start,
                    self.stream.current_string_start_index(),
                ));
            }
            TT::While | TT::For | TT::If => {
                return self.flow_controll(indentation, vars, global_vars, all_vars, imported, false);
            }
            _ => {}
        }
        let node2 = self.tuple_or_expression(false, TT::Assign, None, true)?;
        if self.cur() == TT::Assign {
            return self.assignment(node2, vars, global_vars, all_vars);
        }
        if let NK::Value(value) = &node2.kind {
            if is_builtin_name(value) {
                return self.perr(&err("error_not_a_statement2", &[format!("{}()", value)]), node2.start);
            }
        }
        Ok(node2)
    }

    fn sequence_of_identifiers(&mut self, error: Option<&str>) -> R<Vec<String>> {
        let mut list = Vec::new();
        if self.cur() == TT::BracketOpen {
            self.consume(TT::BracketOpen, None)?;
            self.line_breaks();
            list.push(self.consume(TT::Identifier, error)?.value);
            self.line_breaks();
            loop {
                if self.cur() == TT::Comma {
                    self.consume(TT::Comma, None)?;
                    self.line_breaks();
                    if self.cur() == TT::BracketClose {
                        self.consume(TT::BracketClose, None)?;
                        break;
                    }
                    list.push(self.consume(TT::Identifier, error)?.value);
                    self.line_breaks();
                    continue;
                }
                self.consume(TT::BracketClose, error)?;
                break;
            }
        } else {
            list.push(self.consume(TT::Identifier, error)?.value);
            while self.cur() == TT::Comma {
                self.consume(TT::Comma, None)?;
                list.push(self.consume(TT::Identifier, error)?.value);
            }
            if let Some(e) = error {
                if self.stream.current().is_some() && self.cur() != TT::NewLine {
                    return self.perr(e, self.stream.current_string_start_index());
                }
            }
        }
        Ok(list)
    }

    fn assignment(&mut self, lhs: PN, vars: &SetRef, global_vars: &SetRef, all_vars: &SetRef) -> R<PN> {
        let token = self.consume(TT::Assign, None)?;
        let item = self.tuple_or_expression(false, TT::BracketClose, None, false)?;
        self.check_assignment_lhs_rec(&lhs, vars, global_vars, all_vars)?;
        Ok(PN::with(
            NK::Assignment(Rc::from(token.value.as_str())),
            token.start,
            token.start + token.value.len(),
            vec![lhs, item],
        ))
    }

    fn check_assignment_lhs_rec(&self, lhs: &PN, vars: &SetRef, global_vars: &SetRef, all_vars: &SetRef) -> R<()> {
        match &lhs.kind {
            NK::Value(value) => {
                if ALL_KEY_WORDS.contains(&value.as_ref()) || evaluate_constant(value).is_some() {
                    return self.perr(&err("error_reserved_keyword", &[value.to_string()]), lhs.start);
                }
                if !global_vars.borrow().contains(value.as_ref()) {
                    vars.borrow_mut().insert(value.to_string());
                }
                all_vars.borrow_mut().insert(value.to_string());
                Ok(())
            }
            NK::Tuple | NK::List => {
                for slot in lhs.slots[0].slots.iter() {
                    self.check_assignment_lhs_rec(slot, vars, global_vars, all_vars)?;
                }
                Ok(())
            }
            NK::Bracket => self.check_assignment_lhs_rec(&lhs.slots[0], vars, global_vars, all_vars),
            NK::Binary(op, _, _) if op.as_ref() == "." || (op.as_ref() == "[]" && lhs.slots[1].slots.len() == 1) => Ok(()),
            _ => self.perr("error_invalid_assign_expr", lhs.start),
        }
    }

    fn flow_controll(&mut self, indentation: i32, vars: &SetRef, global_vars: &SetRef, all_vars: &SetRef, imported: &SetRef, is_elif: bool) -> R<PN> {
        let mut flag = false;
        let mut pattern: Option<PN> = None;
        let mut node;
        if self.cur() == TT::While {
            let t = self.consume(TT::While, None)?;
            node = PN::new(NK::Branch(true), t.start, t.start + t.value.len());
        } else if self.cur() == TT::For {
            let t = self.consume(TT::For, None)?;
            let node2 = self.tuple_or_expression(false, TT::In, None, false)?;
            self.check_assignment_lhs_rec(&node2, vars, global_vars, all_vars)?;
            node = PN::new(NK::For, t.start, t.start + t.value.len());
            self.consume(TT::In, Some("error_invalid_for_syntax"))?;
            pattern = Some(node2);
        } else {
            let t = self.consume(if is_elif { TT::Elif } else { TT::If }, None)?;
            node = PN::new(NK::Branch(false), t.start, t.start + t.value.len());
            flag = true;
        }
        let item = self.tuple_or_expression(false, TT::BracketClose, None, false)?;
        if self.cur() == TT::Assign {
            return self.perr("error_unexpected_assign", self.stream.current_string_start_index());
        }
        self.consume_colon()?;
        let item2 = self.block(indentation, vars, global_vars, all_vars, imported, false, false)?;
        node.slots.push(item);
        node.slots.push(item2);
        if let Some(p) = pattern {
            node.slots.push(p);
        }
        if flag && self.stream.look_ahead_ty() == TT::Else && self.get_indentation()? == indentation {
            self.consume(TT::NewLine, Some("error_new_line_expected"))?;
            self.consume(TT::Else, None)?;
            self.consume_colon()?;
            node.slots.push(self.block(indentation, vars, global_vars, all_vars, imported, false, false)?);
            return Ok(node);
        }
        if flag && self.stream.look_ahead_ty() == TT::Elif && self.get_indentation()? == indentation {
            self.consume(TT::NewLine, Some("error_new_line_expected"))?;
            node.slots.push(self.flow_controll(indentation, vars, global_vars, all_vars, imported, true)?);
        }
        Ok(node)
    }

    /// Parser.Sequence; returns (node, keyValuePairs)
    fn sequence(&mut self, end_token: TT, allow_key_value_pairs: bool, line_breaks: bool) -> R<(PN, bool)> {
        let mut key_value_pairs = true;
        let mut node = PN::new(NK::Seq, 0, 0);
        if line_breaks {
            self.line_breaks();
        }
        if self.cur() == end_token && self.stream.current().is_some() {
            return Ok((node, key_value_pairs));
        }
        let cur_is_newline = self.cur() == TT::NewLine;
        if !((!cur_is_newline || line_breaks) && (self.stream.current().is_some() || line_breaks)) {
            return Ok((node, key_value_pairs));
        }
        loop {
            let item = self.expression(0, line_breaks, end_token, false)?;
            if line_breaks {
                self.line_breaks();
            }
            if self.cur() == TT::Colon {
                if !key_value_pairs || !allow_key_value_pairs {
                    return self.perr("error_invalid_expression", self.stream.current_string_start_index());
                }
                self.consume(TT::Colon, Some("error_wrong_dict_literal"))?;
                if line_breaks {
                    self.line_breaks();
                }
                let item2 = self.expression(0, line_breaks, end_token, false)?;
                node.slots.push(item);
                node.slots.push(item2);
            } else {
                if key_value_pairs && !node.slots.is_empty() {
                    return self.perr("error_invalid_expression", self.stream.current_string_start_index());
                }
                node.slots.push(item);
                key_value_pairs = false;
            }
            if line_breaks {
                self.line_breaks();
            }
            let flag = self.cur() == TT::Comma;
            if flag {
                self.consume(TT::Comma, None)?;
                if line_breaks {
                    self.line_breaks();
                }
            }
            let flag2 = if self.stream.current().is_some() && self.cur() == end_token {
                true
            } else if self.cur() == TT::NewLine && !line_breaks {
                true
            } else {
                self.stream.current().is_none() && !line_breaks
            };
            if flag2 {
                break;
            }
            if !flag {
                let key = if line_breaks { "error_expected_close_token" } else { "error_invalid_expression" };
                return self.perr(key, self.stream.current_string_start_index());
            }
        }
        Ok((node, key_value_pairs))
    }

    fn tuple_or_expression(&mut self, can_line_break: bool, end_of_tuple: TT, start_expr: Option<PN>, is_leftmost: bool) -> R<PN> {
        if start_expr.is_none() && self.stream.current().is_some() && self.cur() == end_of_tuple {
            let p = self.stream.current_string_start_index();
            return Ok(PN::with(NK::Tuple, p, p, vec![PN::new(NK::Seq, 0, 0)]));
        }
        let node = match start_expr {
            Some(n) => n,
            None => self.expression(0, can_line_break, end_of_tuple, is_leftmost)?,
        };
        if self.cur() == TT::Comma {
            self.consume(TT::Comma, None)?;
            let (mut node2, _) = self.sequence(end_of_tuple, false, can_line_break)?;
            node2.slots.insert(0, node);
            let p = self.stream.current_string_start_index();
            return Ok(PN::with(NK::Tuple, p, p, vec![node2]));
        }
        Ok(node)
    }

    fn expression(&mut self, mut op_index: usize, can_line_break: bool, exclude_token: TT, is_leftmost: bool) -> R<PN> {
        if can_line_break {
            self.line_breaks();
        }
        if op_index < OPERATORS.len() && OPERATORS[op_index].0.contains(&exclude_token) {
            op_index += 1;
        }
        if op_index < OPERATORS.len() {
            return match OPERATORS[op_index].1 {
                0 => self.binary_expression(op_index, can_line_break, exclude_token, is_leftmost),
                1 => self.unary_expression(op_index, can_line_break, exclude_token, is_leftmost),
                _ => self.index_dot_or_call_expression(op_index, can_line_break, exclude_token, is_leftmost),
            };
        }
        self.atomic_expression(is_leftmost)
    }

    fn line_breaks(&mut self) {
        while self.cur() == TT::NewLine {
            self.stream.tokens.pop_front();
        }
    }

    fn optional_variable_type_annotation(&mut self) -> R<()> {
        if self.cur() != TT::Colon {
            return Ok(());
        }
        let la = self.stream.look_ahead_ty();
        if la != TT::Str && la != TT::Identifier {
            return Ok(());
        }
        self.consume(TT::Colon, None)?;
        self.type_expression(false)
    }
    fn optional_return_type_annotation(&mut self) -> R<()> {
        if self.cur() == TT::Arrow {
            self.consume(TT::Arrow, None)?;
            self.type_expression(false)?;
        }
        Ok(())
    }
    fn optional_generic_type_annotation(&mut self) -> R<()> {
        if self.cur() == TT::SquareBracketOpen {
            self.type_expression_list()?;
        }
        Ok(())
    }
    fn type_expression(&mut self, identifier_is_optional: bool) -> R<()> {
        if self.cur() == TT::Str {
            self.consume(TT::Str, None)?;
            return Ok(());
        }
        if identifier_is_optional {
            if self.cur() == TT::Identifier {
                self.consume(TT::Identifier, None)?;
            }
        } else {
            self.consume(TT::Identifier, None)?;
        }
        if self.cur() == TT::SquareBracketOpen {
            self.type_expression_list()?;
        }
        if self.cur() == TT::Union {
            self.consume(TT::Union, None)?;
            self.type_expression(false)?;
        }
        Ok(())
    }
    fn type_expression_list(&mut self) -> R<()> {
        self.consume(TT::SquareBracketOpen, None)?;
        if self.cur() == TT::BracketOpen {
            self.consume(TT::BracketOpen, None)?;
            self.consume(TT::BracketClose, None)?;
        } else {
            self.type_expression(true)?;
            while self.cur() == TT::Comma {
                self.consume(TT::Comma, None)?;
                if self.cur() == TT::SquareBracketClose {
                    break;
                }
                self.type_expression(true)?;
            }
        }
        self.consume(TT::SquareBracketClose, None)?;
        Ok(())
    }

    fn bracket_expression(&mut self) -> R<PN> {
        self.consume(TT::BracketOpen, None)?;
        let node = self.tuple_or_expression(true, TT::BracketClose, None, false)?;
        self.line_breaks();
        self.consume(TT::BracketClose, None)?;
        Ok(PN::with(NK::Bracket, node.start, node.end, vec![node]))
    }

    fn binary_expression(&mut self, op_index: usize, can_line_break: bool, exclude_token: TT, is_leftmost: bool) -> R<PN> {
        if can_line_break {
            self.line_breaks();
        }
        let node = self.expression(op_index + 1, can_line_break, exclude_token, is_leftmost)?;
        if can_line_break {
            self.line_breaks();
        }
        let types = OPERATORS[op_index].0;
        for item in types.iter() {
            if self.cur() != *item {
                continue;
            }
            if *item == TT::Compare || *item == TT::In {
                let start = node.start;
                let mut list = vec![node];
                let mut list2: Vec<Rc<str>> = Vec::new();
                while self.cur() == TT::Compare || self.cur() == TT::In {
                    let token = self.consume_any()?;
                    list.push(self.binary_expression(op_index + 1, can_line_break, exclude_token, false)?);
                    list2.push(Rc::from(token.value.as_str()));
                }
                let cops = list2.iter().map(|o| COp::of(o)).collect();
                return Ok(PN::with(NK::Comparison(list2, cops), start, self.stream.current_string_end_index(), list));
            }
            let token2 = self.consume(*item, None)?;
            let mut node2 = self.binary_expression(op_index, can_line_break, exclude_token, false)?;
            let mut node3 = PN::new(
                NK::Binary(Rc::from(token2.value.as_str()), token2.ty, BOp::of(&token2.value)),
                token2.start,
                token2.start + token2.value.len(),
            );
            node3.slots.push(node);
            let same_level = |n: &PN| matches!(&n.kind, NK::Binary(_, t, _) if types.contains(t));
            if !same_level(&node2) {
                node3.slots.push(node2);
                return Ok(node3);
            }
            // Re-hang the right-recursive parse so the operators associate to the left.
            let mut node4: &mut PN = &mut node2;
            while same_level(&node4.slots[0]) {
                node4 = &mut node4.slots[0];
            }
            let left = std::mem::replace(&mut node4.slots[0], PN::new(NK::Pass, 0, 0));
            node3.slots.push(left);
            node4.slots[0] = node3;
            return Ok(node2);
        }
        Ok(node)
    }

    fn unary_expression(&mut self, op_index: usize, can_line_break: bool, exclude_token: TT, is_leftmost: bool) -> R<PN> {
        if can_line_break {
            self.line_breaks();
        }
        for item2 in OPERATORS[op_index].0.iter() {
            if self.cur() == *item2 {
                let token = self.consume(*item2, None)?;
                let item = self.expression(op_index, can_line_break, TT::NoToken, false)?;
                return Ok(PN::with(
                    NK::Unary(Rc::from(token.value.as_str())),
                    token.start,
                    token.start + token.value.len(),
                    vec![item],
                ));
            }
        }
        self.expression(op_index + 1, can_line_break, exclude_token, is_leftmost)
    }

    fn index_dot_or_call_expression(&mut self, op_index: usize, can_line_break: bool, exclude_token: TT, is_leftmost: bool) -> R<PN> {
        if can_line_break {
            self.line_breaks();
        }
        let mut node = self.expression(op_index + 1, can_line_break, exclude_token, is_leftmost)?;
        if can_line_break {
            self.line_breaks();
        }
        loop {
            match self.cur() {
                TT::SquareBracketOpen => {
                    let token = self.consume(TT::SquareBracketOpen, None)?;
                    let mut node2 = PN::new(NK::Seq, 0, 0);
                    node2.slots.push(self.slice_index(false)?);
                    if self.cur() == TT::Colon {
                        self.consume(TT::Colon, None)?;
                        node2.slots.push(self.slice_index(true)?);
                        if self.cur() == TT::Colon {
                            self.consume(TT::Colon, None)?;
                            self.line_breaks();
                            if self.cur() != TT::SquareBracketClose {
                                node2.slots.push(self.expression(0, true, TT::NoToken, false)?);
                            }
                        }
                    }
                    self.line_breaks();
                    self.consume(TT::SquareBracketClose, None)?;
                    node = PN::with(
                        NK::Binary(Rc::from("[]"), TT::BracketOpen, BOp::Index),
                        token.start,
                        token.start + token.value.len(),
                        vec![node, node2],
                    );
                }
                TT::BracketOpen => {
                    let token2 = self.consume(TT::BracketOpen, None)?;
                    let (item, _) = self.sequence(TT::BracketClose, false, true)?;
                    self.consume(TT::BracketClose, None)?;
                    node = PN::with(NK::Call, token2.start, token2.start + token2.value.len(), vec![node, item]);
                }
                TT::Dot => {
                    let token3 = self.consume(TT::Dot, None)?;
                    let token4 = self.consume(TT::Identifier, None)?;
                    if let NK::Literal(V::Bag(ns)) = &node.kind {
                        match bag_evaluate(*ns, &token4.value) {
                            Ok(v) => {
                                node = PN::new(NK::Literal(v), node.start, token4.start + token4.value.len());
                            }
                            Err(e) => return self.perr(&e, node.start),
                        }
                    } else {
                        let item2 = PN::new(
                            NK::Value(intern(token4.value.as_str())),
                            token4.start,
                            token4.start + token4.value.len(),
                        );
                        node = PN::with(
                            NK::Binary(Rc::from("."), TT::Dot, BOp::Dot),
                            token3.start,
                            token3.start + token3.value.len(),
                            vec![node, item2],
                        );
                    }
                }
                _ => break,
            }
        }
        Ok(node)
    }

    fn slice_index(&mut self, could_be_last_slice: bool) -> R<PN> {
        self.line_breaks();
        let node;
        if self.cur() != TT::Colon && !(self.cur() == TT::SquareBracketClose && could_be_last_slice) {
            let mut n = self.expression(0, true, TT::NoToken, false)?;
            if self.cur() != TT::Colon {
                n = self.tuple_or_expression(true, TT::SquareBracketClose, Some(n), false)?;
            }
            node = n;
        } else {
            let p = self.stream.current_string_start_index();
            node = PN::new(NK::Literal(V::None), p, p);
        }
        self.line_breaks();
        Ok(node)
    }

    fn atomic_expression(&mut self, can_be_type_annotated: bool) -> R<PN> {
        match self.cur() {
            TT::BracketOpen => self.bracket_expression(),
            TT::SquareBracketOpen => {
                let s = self.stream.current_string_start_index();
                let e = self.stream.current_string_end_index();
                self.consume(TT::SquareBracketOpen, None)?;
                let (item, _) = self.sequence(TT::SquareBracketClose, false, true)?;
                self.consume(TT::SquareBracketClose, None)?;
                Ok(PN::with(NK::List, s, e, vec![item]))
            }
            TT::CurlBraceOpen => {
                let s = self.stream.current_string_start_index();
                let e = self.stream.current_string_end_index();
                self.consume(TT::CurlBraceOpen, None)?;
                let (item2, kv) = self.sequence(TT::CurlBraceClose, true, true)?;
                self.consume(TT::CurlBraceClose, None)?;
                Ok(PN::with(if kv { NK::Dict } else { NK::Set }, s, e, vec![item2]))
            }
            TT::Num => {
                let token = self.consume(TT::Num, None)?;
                let num: f64 = match token.value.parse::<f64>() {
                    Ok(n) => n,
                    Err(_) => return self.perr("error_invalid_number_format", token.start),
                };
                Ok(PN::new(NK::Literal(V::Num(num)), token.start, token.start + token.value.len()))
            }
            TT::Str => {
                let token2 = self.consume(TT::Str, None)?;
                let chars: Vec<char> = token2.value.chars().collect();
                let inner: String = chars[1..chars.len() - 1].iter().collect();
                Ok(PN::new(NK::Literal(new_str(&inner)), token2.start, token2.start + chars.len()))
            }
            TT::Identifier => {
                let token3 = self.consume(TT::Identifier, None)?;
                if can_be_type_annotated {
                    self.optional_variable_type_annotation()?;
                }
                let end = token3.start + token3.value.chars().count();
                if let Some(v) = evaluate_constant(&token3.value) {
                    return Ok(PN::new(NK::Literal(v), token3.start, end));
                }
                Ok(PN::new(NK::Value(intern(token3.value.as_str())), token3.start, end))
            }
            _ => self.perr("error_invalid_expression", self.stream.current_string_start_index()),
        }
    }

    fn get_indentation(&mut self) -> R<i32> {
        if self.cur() != TT::NewLine {
            return self.perr("error_new_line_expected", self.stream.current_string_start_index());
        }
        while self.stream.look_ahead_ty() == TT::NewLine {
            self.stream.tokens.pop_front();
        }
        let value = &self.stream.current().unwrap().value;
        if value.contains('\t') && value.contains(' ') {
            return self.perr("error_mixed_indentation", self.stream.current_string_start_index() + 1);
        }
        Ok((value.matches(' ').count() + value.matches('\t').count() * 4) as i32)
    }

    fn consume_colon(&mut self) -> R<Token> {
        if self.cur() == TT::NewLine {
            return self.perr("error_missing_colon", self.stream.current_string_start_index());
        }
        self.consume(TT::Colon, None)
    }
}

/// CodeWindow.Parse
thread_local! {
    static PARSED: RefCell<HashMap<(String, String), Rc<Node>>> = RefCell::new(HashMap::new());
}
/// parse_source, once per (module name, source text) on each thread: runs never change a tree
/// (only the lookup caches in it, which hold for any run).
fn parse_source(name: &str, code: &str) -> R<Rc<Node>> {
    let k = (name.to_string(), code.to_string());
    if let Some(t) = PARSED.with(|p| p.borrow().get(&k).cloned()) {
        return Ok(t);
    }
    let t = parse_source_uncached(name, code)?;
    PARSED.with(|p| p.borrow_mut().insert(k, t.clone()));
    Ok(t)
}

fn parse_source_uncached(name: &str, code: &str) -> R<Rc<Node>> {
    let text = code.replace('\u{0B}', "\n");
    let mut line_starts = vec![0usize];
    for (i, c) in text.chars().enumerate() {
        if c == '\n' {
            line_starts.push(i + 1);
        }
    }
    let file = Rc::new(FileInfo { name: name.to_string(), line_starts });
    let stream = tokenize(code).map_err(|e| format!("{}.py {}", name, e))?;
    Parser { stream, file }.parse()
}

// ---------------------------------------------------------------------------------------------
// ProgramState
// ---------------------------------------------------------------------------------------------
enum Ctrl {
    Break,
    Continue,
    Return,
    Err(String),
}
impl From<String> for Ctrl {
    fn from(s: String) -> Ctrl {
        Ctrl::Err(s)
    }
}
type Res = Result<(), Ctrl>;
/// a node's value, or how its evaluation was cut short
type Ev = Result<V, Ctrl>;
/// One C# IEnumerator<double>: resuming it is MoveNext(), a yield is `yield return`.

#[derive(Clone)]
enum SE {
    None,
    Harvest,
    CanHarvest,
    Swap(u8),
    Plant(&'static str),
    Move(u8),
    CanMove(u8),
    Till,
    GetPosX,
    GetPosY,
    GetPosZ,
    GetWorldSize,
    GetEntityType(Option<u8>),
    GetGroundType(Option<u8>),
    UseItem(&'static str, i32),
    GetWater,
    ChangeHat(&'static str),
    NumItems(&'static str),
    GetCost(V, Option<V>),
    Clear,
    GetCompanion,
    Unlock(&'static str),
    NumUnlocked(V),
    Measure(Option<u8>),
    SetExecutionSpeed(f64),
    SetWorldSize(f64),
    GetTime,
    SpawnDrone(Vec<V>),
    NumDrones,
    MaxDrones,
    Await(Rc<DroneHandle>),
    HasFinished(Rc<DroneHandle>),
    Terminated,
    Error,
    DoAFlip,
    PetThePiggy,
    Print(String),
    NotPorted(&'static str),
}

struct ModuleState {
    global_scope: ScopeRef,
    call_stack: Vec<ScopeRef>,
    return_value: V,
    is_expression_static: bool,
}

/// The bits of Simulation / MainSim the interpreter itself reads.
/// Where print / quick_print go: straight to stdout, into the run's report (when several runs
/// share the terminal), or nowhere (--quiet).
#[derive(Clone, Copy, PartialEq)]
enum Echo {
    Live,
    Buffered,
    Off,
}

struct Shared {
    op_duration_ns: Cell<i64>,
    current_time: Cell<i64>,
    echo: Echo,
    dir: std::path::PathBuf,
    output: RefCell<Vec<String>>,
    warnings: RefCell<HashMap<String, u64>>,
    /// Execution.leaderboardCodeNodeCount; None outside a leaderboard run, where nothing is counted
    lb_nodes: Cell<Option<usize>>,
    /// Execution.leaderboardCodeModules
    lb_modules: RefCell<HashSet<String>>,
    /// every syntax tree the run has parsed (main file and imports)
    trees: RefCell<Vec<Rc<Node>>>,
}

/// Execution.RegisterLeaderboardCode: a leaderboard run may hold at most 100,000 syntax nodes,
/// counted over the main file and every module it imports (each module once).
const LEADERBOARD_CODE_LIMIT: usize = 100000;
fn register_leaderboard_code(sh: &Shared, module_name: &str, tree: &Rc<Node>) -> R<()> {
    let mut count = match sh.lb_nodes.get() {
        Some(c) => c,
        None => return Ok(()),
    };
    if count <= LEADERBOARD_CODE_LIMIT && !sh.lb_modules.borrow_mut().insert(module_name.to_string()) {
        return Ok(());
    }
    let mut stack: Vec<Rc<Node>> = vec![tree.clone()];
    while let Some(node) = stack.pop() {
        if count > LEADERBOARD_CODE_LIMIT {
            break;
        }
        count += 1;
        for slot in node.slots.iter() {
            stack.push(slot.clone());
        }
    }
    sh.lb_nodes.set(Some(count));
    if count <= LEADERBOARD_CODE_LIMIT {
        return Ok(());
    }
    Err("error_leaderboard_code_too_large".into())
}

impl Shared {
    fn log(&self, msg: &str) {
        let line = format!("[{:10.3}s] {}", dur_seconds(self.current_time.get()), msg);
        match self.echo {
            Echo::Live => println!("{}", line),
            Echo::Buffered => self.output.borrow_mut().push(line),
            Echo::Off => {}
        }
    }
    fn warn(&self, msg: String) {
        *self.warnings.borrow_mut().entry(msg).or_insert(0) += 1;
    }
}

/// What the scheduler reads for every drone on every pass, kept for all drones in one array
/// (Execution::hot) so that a pass over them reads a few cache lines instead of every drone's state.
#[derive(Clone, Copy)]
struct Hot {
    op_count: f64,
    target_op_count: f64,
    last_consumed_op_count: f64,
    awaited_drone_id: i32,
    /// resumes in the current PerformExecutionStep (the game stops at 1000)
    resumes: i32,
    /// the kind of current_side_effect: SE_NONE, SE_GET_TIME, SE_NUM_ITEMS or SE_OTHER
    se: u8,
    /// a drone is in this slot
    present: bool,
}
const SE_NONE: u8 = 0;
const SE_GET_TIME: u8 = 1;
const SE_NUM_ITEMS: u8 = 2;
const SE_OTHER: u8 = 3;
const HOT_EMPTY: Hot = Hot { op_count: 0.0, target_op_count: 0.0, last_consumed_op_count: 0.0, awaited_drone_id: -1, resumes: 0, se: SE_NONE, present: false };

struct PState {
    /// this drone's slot in Execution::hot (which never moves while the execution lasts)
    hot: *mut Hot,
    current_side_effect: SE,
    sh: Rc<Shared>,
    module_state: ModuleState,
    current_execute_exception: Option<String>,
    random_random: SysRandom,
    /// the program; None until the drone's state is set up (and while it runs)
    program: Option<Box<Vm>>,
    /// skip_busy_waits' last answer for this drone: (deadline bits, clock origin, op duration,
    /// first op count that reads the deadline)
    wait_cache: (u64, i64, i64, f64),
    /// ProgramState's execution stack, as a count: 1 for the program, +1 per user function call
    /// still running; 0 once the program has ended
    frames: usize,
    module_cache: HashMap<String, Rc<PyModule>>,
    start_op_count: f64,
    drone_id: i32,
    drone_handle: Option<Rc<DroneHandle>>,
    /// the node being run, for error reports; the trees it points into are kept alive by
    /// Shared::trees for the whole run
    current_executing_node: *const Node,
    /// Set while this drone is asking for the time in the condition of `while get_time() < x: pass`
    /// (second pass onwards): the value of x. Execute uses it to skip the passes that cannot end.
    wait_deadline: Option<f64>,
    /// Set while this drone reads the count in the condition of `while num_items(i) < x: pass`
    /// (any one comparison, second pass onwards). Execute uses it, with `spin_read` and
    /// `spin_period`, to skip the passes that read an unchanged count.
    spin_loop: bool,
    /// The last count read in that loop: the op count it was read at and the value.
    spin_read: Option<(f64, f64)>,
    /// Ops from one read to the next, once two reads have been seen.
    spin_period: Option<f64>,
}
type StRef = Rc<RefCell<PState>>;

static FUNCTION_LIST: &[(&str, bool)] = &[
    ("harvest", false), ("can_harvest", false), ("swap", false), ("range", false), ("plant", false), ("move", false),
    ("can_move", false), ("till", false), ("get_pos_x", false), ("get_pos_y", false), ("get_pos_z", false),
    ("get_world_size", false), ("get_entity_type", false), ("get_ground_type", false), ("get_time", true),
    ("get_tick_count", true), ("use_item", false), ("place", false), ("get_water", false), ("do_a_flip", false),
    ("change_hat", false), ("print", false), ("quick_print", true), ("len", false), ("num_items", false),
    ("get_cost", false), ("clear", false), ("get_companion", false), ("unlock", false), ("num_unlocked", false),
    ("leaderboard_run", false), ("measure", false), ("min", false), ("max", false), ("abs", false), ("str", false),
    ("random", false), ("simulate", false), ("list", false), ("set", false), ("dict", false),
    ("set_execution_speed", false), ("set_world_size", false), ("spawn_drone", false), ("num_drones", false),
    ("max_drones", false), ("wait_for", false), ("has_finished", false), ("pet_the_piggy", false), ("tap", false),
    ("dig", false), ("get_hardness", false), ("get_stability", false), ("prospect_iron", false),
    ("prospect_quartz", false), ("push", false), ("can_push", false), ("jump", false), ("hover", false),
    ("get_hover", false),
    // methodList
    ("append", false), ("add", false), ("remove", false), ("pop", false), ("insert", false),
];

fn is_builtin_name(name: &str) -> bool {
    FUNCTION_LIST.iter().any(|(n, _)| *n == name)
}

/// The global scope every ProgramState and module starts with: __name__ plus all builtins as statics.
fn register_builtins(scope: &ScopeRef) {
    for (name, is_free) in FUNCTION_LIST.iter() {
        let f = Rc::new(PyFunc {
            name: Rc::from(*name),
            syntax_tree: None,
            parent_scope: None,
            binding: Some(name),
            method_object: None,
            is_free: *is_free,
        });
        scope_set_var(scope, &intern(name), V::Func(f), true);
    }
}

impl PState {
    fn new(op_count: f64, random: &mut SysRandom, drone_id: i32, sh: Rc<Shared>) -> PState {
        let global_scope = new_scope(None, None, &[]);
        scope_import_var(&global_scope, &intern("__name__"), new_str("__main__"), false);
        PState {
            sh,
            module_state: ModuleState {
                global_scope,
                call_stack: Vec::new(),
                return_value: V::None,
                is_expression_static: false,
            },
            hot: std::ptr::null_mut(),
            current_side_effect: SE::None,
            current_execute_exception: None,
            random_random: SysRandom::new(random.next()),
            program: None,
            wait_cache: (0, 0, 0, f64::NAN),
            frames: 1,
            module_cache: HashMap::new(),
            start_op_count: op_count,
            drone_id,
            drone_handle: None,
            current_executing_node: std::ptr::null(),
            wait_deadline: None,
            spin_loop: false,
            spin_read: None,
            spin_period: None,
        }
    }
    fn current_scope(&self) -> ScopeRef {
        match self.module_state.call_stack.last() {
            Some(s) => s.clone(),
            None => self.module_state.global_scope.clone(),
        }
    }
    #[inline(always)]
    fn h(&self) -> &mut Hot {
        unsafe { &mut *self.hot }
    }
    fn has_side_effect(&self) -> bool {
        self.h().se != SE_NONE
    }
    /// sets current_side_effect, keeping its kind in the hot record
    fn set_se(&mut self, se: SE) {
        self.h().se = match &se {
            SE::None => SE_NONE,
            SE::GetTime => SE_GET_TIME,
            SE::NumItems(_) => SE_NUM_ITEMS,
            _ => SE_OTHER,
        };
        self.current_side_effect = se;
    }
    fn add_and_consume_ops(&mut self, ops: f64) {
        self.h().op_count += ops;
        self.h().last_consumed_op_count += ops;
    }
    fn consume_ops(&mut self) -> f64 {
        let result = self.h().op_count - self.h().last_consumed_op_count;
        self.h().last_consumed_op_count = self.h().op_count;
        result
    }
}

/// The drone's state, for the leaf helpers below. They never call out while holding it, and a
/// drone's state is only ever touched by its own program or by the scheduler while the program is
/// suspended, so the RefCell check would never fire here.
#[inline(always)]
fn stm(st: &StRef) -> &mut PState {
    unsafe { &mut *st.as_ptr() }
}
#[inline]
fn rv(st: &StRef) -> V {
    stm(st).module_state.return_value.clone()
}
#[inline]
fn set_rv(st: &StRef, v: V) {
    stm(st).module_state.return_value = v;
}
#[inline]
fn set_static(st: &StRef, b: bool) {
    stm(st).module_state.is_expression_static = b;
}

/// Node.CheckIncrementOpCount
#[inline]
fn check_inc(st: &StRef, ops: f64) -> bool {
    let s = stm(st);
    s.h().op_count += ops;
    s.h().op_count >= s.h().target_op_count || s.has_side_effect()
}

/// Node.ErrorsAndBreakpoints (breakpoints, step mode and unlock checks are not needed headless)
fn eb(st: &StRef, node: &Rc<Node>, depth: i32) -> R<()> {
    if depth > 1100 {
        return Err("error_max_stack_size_reached".into());
    }
    stm(st).current_executing_node = Rc::as_ptr(node);
    Ok(())
}

/// ProgramState.PushOntoExecutionStack, for a user function call
fn push_frame(st: &StRef) -> R<()> {
    let mut s = st.borrow_mut();
    if s.frames >= 1101 {
        return Err("error_max_stack_size_reached".into());
    }
    s.frames += 1;
    Ok(())
}

/// A point where the game's iterator yields. PerformExecutionStep resumes the program again right
/// away unless it is past its target op count, has a side effect for the scheduler, or has
/// already been resumed 1000 times this step; otherwise the drone hands back to the scheduler.
#[inline]
fn yp(st: &StRef) {
    let stop = {
        let s = stm(st);
        s.h().resumes += 1;
        !(s.h().op_count <= s.h().target_op_count) || s.has_side_effect() || s.h().resumes >= 1000
    };
    if stop {
        stacks::suspend();
    }
}

/// How a drone's program ends: ProgramState.PerformExecutionStep's handling of the last iterator.
fn program_finished(st: &StRef, r: Res) {
    let mut s = st.borrow_mut();
    s.frames = 0;
    if let Err(c) = r {
        s.current_execute_exception = Some(match c {
            Ctrl::Break => "error_no_loop_to_break".to_string(),
            Ctrl::Continue => "error_no_loop_to_continue".to_string(),
            Ctrl::Return => "error_no_function_to_return_from".to_string(),
            Ctrl::Err(e) => e,
        });
        s.set_se(SE::Error);
    }
}

/// ProgramState.PerformExecutionStep
fn perform_execution_step(st: &StRef, target_op_count: f64) {
    let mut vm = {
        let mut s = st.borrow_mut();
        s.h().target_op_count = target_op_count;
        if s.frames == 0 {
            s.set_se(SE::Terminated);
            return;
        }
        if s.h().awaited_drone_id >= 0 {
            s.h().op_count += 1.0;
            s.h().last_consumed_op_count += 1.0;
            return;
        }
        s.h().resumes = 0;
        match s.program.take() {
            Some(p) => p,
            None => return,
        }
    };
    vm_run(st, &mut vm);
    stm(st).program = Some(vm);
}

// ---------------------------------------------------------------------------------------------
// Node.Execute for every node type
// ---------------------------------------------------------------------------------------------

fn is_literal_node(node: &Rc<Node>) -> Option<V> {
    let mut n = node;
    while let NK::Bracket = &n.kind {
        if n.slots.is_empty() {
            break;
        }
        n = &n.slots[0];
    }
    match &n.kind {
        NK::Literal(v) => Some(v.clone()),
        _ => None,
    }
}

/// The name x if this loop is exactly `while get_time() < x: pass`, the busy-wait scripts use to
/// act at a set time. Every pass of it costs two ops and changes nothing but the drone's op count.
fn busy_wait_name(node: &Rc<Node>) -> Option<Rc<str>> {
    if node.slots.len() != 2 {
        return None;
    }
    let cond = &node.slots[0];
    match &cond.kind {
        NK::Comparison(ops, _) if ops.len() == 1 && ops[0].as_ref() == "<" && cond.slots.len() == 2 => {}
        _ => return None,
    }
    let call = &cond.slots[0];
    let is_get_time = matches!(&call.kind, NK::Call)
        && call.slots.len() == 2
        && matches!(&call.slots[0].kind, NK::Value(v) if v.as_ref() == "get_time")
        && call.slots[1].slots.is_empty();
    if !is_get_time {
        return None;
    }
    if !body_only_pass(node) {
        return None;
    }
    match &cond.slots[1].kind {
        NK::Value(name) if !is_builtin_name(name) => Some(name.clone()),
        _ => None,
    }
}

fn body_only_pass(node: &Rc<Node>) -> bool {
    let body = &node.slots[1];
    match &body.kind {
        NK::Pass => true,
        NK::Seq => body.slots.len() == 1 && matches!(&body.slots[0].kind, NK::Pass),
        _ => false,
    }
}

fn has_call(node: &Rc<Node>) -> bool {
    matches!(&node.kind, NK::Call) || node.slots.iter().any(has_call)
}

/// `while num_items(i) <op> x: pass` with one comparison, x a literal or a plain variable and i
/// free of calls (e.g. `Items.Power`). Each pass reads the count and nothing else that can change.
fn is_items_spin(node: &Rc<Node>) -> bool {
    if node.slots.len() != 2 || !body_only_pass(node) {
        return false;
    }
    let cond = &node.slots[0];
    match &cond.kind {
        NK::Comparison(ops, _) if ops.len() == 1 && cond.slots.len() == 2 => {}
        _ => return false,
    }
    let is_num_items = |n: &Rc<Node>| {
        matches!(&n.kind, NK::Call)
            && n.slots.len() == 2
            && matches!(&n.slots[0].kind, NK::Value(v) if v.as_ref() == "num_items")
            && n.slots[1].slots.len() == 1
            && !has_call(&n.slots[1].slots[0])
    };
    let is_operand = |n: &Rc<Node>| {
        is_literal_node(n).is_some() || matches!(&n.kind, NK::Value(name) if !is_builtin_name(name))
    };
    let (a, b) = (&cond.slots[0], &cond.slots[1]);
    (is_num_items(a) && is_operand(b)) || (is_num_items(b) && is_operand(a))
}

/// Runs a block of statements (a function body, a loop or branch body, a module). The game's
/// SequenceNode also collects each statement's value into a list, but nothing ever reads a block's
/// value, so it is not built here.
fn exec_block(node: &Rc<Node>, st: &StRef, depth: i32) -> Res {
    if let NK::Seq = &node.kind {
        for slot in node.slots.iter() {
            exec(slot, st, depth + 1)?;
        }
        Ok(())
    } else {
        exec(node, st, depth).map(|_| ())
    }
}

/// Node.Execute: runs a node and returns its value (the game's returnValue).
fn exec(node: &Rc<Node>, st: &StRef, depth: i32) -> Ev {
    {
        {
            match &node.kind {
                NK::Seq => {
                    let mut elements = Vec::with_capacity(node.slots.len());
                    for slot in node.slots.iter() {
                        elements.push(exec(slot, st, depth + 1)?);
                    }
                    Ok(V::Seq(Rc::new(elements)))
                }
                NK::Value(name) => {
                    eb(&st, &node, depth)?;
                    let s = stm(st);
                    let scope = s.module_state.call_stack.last().unwrap_or(&s.module_state.global_scope);
                    let (v, is_static) = scope_lookup(scope, name, Some(&node.lookup))?;
                    s.module_state.is_expression_static = is_static;
                    Ok(v)
                }
                NK::Literal(v) => {
                    eb(&st, &node, depth)?;
                    stm(st).module_state.is_expression_static = false;
                    Ok(v.clone())
                }
                NK::Bracket => exec(&node.slots[0], st, depth + 1),
                NK::Call => {
                    eb(&st, &node, depth)?;
                    let func = match exec(&node.slots[0], st, depth + 1)? {
                        V::Func(f) => f,
                        _ => {
                            st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                            return Err(Ctrl::Err("error_not_a_function".into()));
                        }
                    };
                    let is_static = st.borrow().module_state.is_expression_static;
                    let args = exec(&node.slots[1], st, depth + 1)?;
                    let mut parameters: Vec<V> = match &args {
                        V::Seq(s) => s.to_vec(),
                        _ => Vec::new(),
                    };
                    if let Some(m) = &func.method_object {
                        parameters.insert(0, m.clone());
                    }
                    st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                    if let Some(tree) = &func.syntax_tree {
                        if check_inc(&st, if is_static { 0.0 } else { OPERATION_OPS }) {
                            yp(st);
                        }
                        let vars = match &tree.kind {
                            NK::Function { vars, .. } => vars.clone(),
                            _ => Vec::new(),
                        };
                        let scope = new_scope(Some(tree.clone()), func.parent_scope.clone(), &vars);
                        st.borrow_mut().module_state.call_stack.push(scope);
                        push_frame(st)?;
                        yp(st);
                        let r = exec_function(tree, st, parameters, 0);
                        st.borrow_mut().frames -= 1;
                        return r;
                    }
                    // A builtin's result arrives in returnValue: set by the builtin itself, or by the
                    // scheduler when it applies the side effect. One that sets none leaves the
                    // argument list there, as in the game.
                    stm(st).module_state.return_value = args;
                    let mut num = call_builtin(func.binding.unwrap(), parameters, &st)?;
                    if func.is_free && !is_static {
                        num = num.max(OPERATION_OPS);
                    }
                    if check_inc(&st, num) {
                        yp(st);
                    }
                    Ok(std::mem::replace(&mut stm(st).module_state.return_value, V::None))
                }
                NK::Unary(op) => {
                    eb(&st, &node, depth)?;
                    let value = exec(&node.slots[0], st, depth + 1)?;
                    st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                    if let V::Func(f) = &value {
                        if op.as_ref() != "not" {
                            return Err(Ctrl::Err(err("error_function_in_operator", &[f.name.to_string(), op.to_string()])));
                        }
                    }
                    match op.as_ref() {
                        "+" => {
                            if value.num().is_none() {
                                return Err(Ctrl::Err(err("error_bad_unary_operator", &[op.to_string(), nice_el(&value)])));
                            }
                            Ok(value)
                        }
                        "-" => match value.num() {
                            Some(n) => Ok(V::Num(0.0 - n)),
                            None => {
                                return Err(Ctrl::Err(err("error_bad_unary_operator", &[op.to_string(), nice_el(&value)])))
                            }
                        },
                        _ => {
                            let b = !is_true_value(&value)?;
                            Ok(V::Bool(b))
                        }
                    }
                }
                NK::Binary(op, _, bop) => {
                    let op: &str = op.as_ref();
                    let bop = *bop;
                    eb(&st, &node, depth)?;
                    let lhs = exec(&node.slots[0], st, depth + 1)?;
                    if bop == BOp::And && !is_true_value(&lhs)? {
                        if check_inc(&st, OPERATION_OPS) {
                            yp(st);
                        }
                        return Ok(lhs);
                    }
                    if bop == BOp::Or && is_true_value(&lhs)? {
                        if check_inc(&st, OPERATION_OPS) {
                            yp(st);
                        }
                        return Ok(lhs);
                    }
                    if bop == BOp::Dot && matches!(lhs, V::Module(_) | V::Bag(_)) {
                        let member = match &node.slots[1].kind {
                            NK::Value(v) => v.clone(),
                            _ => return Err(Ctrl::Err("error_invalid_const2".into())),
                        };
                        let is_static = st.borrow().module_state.is_expression_static;
                        if check_inc(&st, if is_static { 0.0 } else { OPERATION_OPS }) {
                            yp(st);
                        }
                        let (v, flag) = match &lhs {
                            V::Module(m) => module_export(m, &member)?,
                            V::Bag(ns) => (bag_evaluate(*ns, &member)?, true),
                            _ => unreachable!(),
                        };
                        stm(st).module_state.is_expression_static &= flag;
                        return Ok(v);
                    }
                    let rhs = exec(&node.slots[1], st, depth + 1)?;
                    st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                    if !matches!(bop, BOp::And | BOp::Or | BOp::Dot) {
                        let f = match (&lhs, &rhs) {
                            (V::Func(f), _) => Some(f.clone()),
                            (_, V::Func(f)) => Some(f.clone()),
                            _ => None,
                        };
                        if let Some(f) = f {
                            return Err(Ctrl::Err(err("error_function_in_operator", &[f.name.to_string(), op.to_string()])));
                        }
                    }
                    let bad = || Ctrl::Err(err("error_bad_bin_operator", &[op.to_string(), nice_el(&lhs), nice_el(&rhs)]));
                    let mut steps: i32 = 0;
                    let result: V = match bop {
                        BOp::And | BOp::Or => {
                            steps = 1;
                            rhs.clone()
                        }
                        BOp::Index => {
                            if !(lhs.is_seq() || matches!(lhs, V::Dict(_))) {
                                return Err(Ctrl::Err(err("error_index_on_non_indexable", &[nice_el(&lhs)])));
                            }
                            let indices = match &rhs {
                                V::Seq(s) => s.clone(),
                                _ => Rc::new(Vec::new()),
                            };
                            index_at(&lhs, &indices, &mut steps, None)?
                        }
                        BOp::Add => {
                            if let (Some(a), Some(b)) = (lhs.num(), rhs.num()) {
                                steps = 1;
                                V::Num(a + b)
                            } else if let (V::List(a), true) = (&lhs, rhs.is_seq()) {
                                let mut out = a.borrow().clone();
                                out.extend(seq_items(&rhs));
                                steps = (out.len() as i32).max(1);
                                new_list(out)
                            } else if let (V::Tuple(a), V::Tuple(b)) = (&lhs, &rhs) {
                                let mut out = a.to_vec();
                                out.extend(b.iter().cloned());
                                steps = (out.len() as i32).max(1);
                                V::Tuple(Rc::new(out))
                            } else if let (V::Str(a), V::Str(b)) = (&lhs, &rhs) {
                                steps = ((a.chars().count() + b.chars().count()) as i32).max(1);
                                new_str(&format!("{}{}", a, b))
                            } else {
                                return Err(bad());
                            }
                        }
                        BOp::Dot => match &rhs {
                            V::Func(f) => {
                                steps = 0;
                                V::Func(Rc::new(PyFunc {
                                    name: f.name.clone(),
                                    syntax_tree: f.syntax_tree.clone(),
                                    parent_scope: f.parent_scope.clone(),
                                    binding: f.binding,
                                    method_object: Some(lhs.clone()),
                                    is_free: f.is_free,
                                }))
                            }
                            _ => return Err(Ctrl::Err("error_unknown_method".into())),
                        },
                        _ => {
                            if matches!(bop, BOp::Div | BOp::FloorDiv | BOp::Mod) && rhs.num() == Some(0.0) {
                                return Err(Ctrl::Err("error_division_by_zero".into()));
                            }
                            let (a, b) = match (lhs.num(), rhs.num()) {
                                (Some(a), Some(b)) => (a, b),
                                _ => return Err(bad()),
                            };
                            steps = 1;
                            V::Num(match bop {
                                BOp::Sub => a - b,
                                BOp::Mul => a * b,
                                BOp::Div => a / b,
                                BOp::FloorDiv => (a / b).floor(),
                                BOp::Mod => py_modulo(a, b),
                                BOp::Pow => a.powf(b),
                                _ => return Err(bad()),
                            })
                        }
                    };
                    if check_inc(&st, OPERATION_OPS * steps as f64) {
                        yp(st);
                    }
                    Ok(result)
                }
                NK::Comparison(ops, cops) => {
                    eb(&st, &node, depth)?;
                    let mut operands = Vec::with_capacity(node.slots.len());
                    for slot in node.slots.iter() {
                        operands.push(exec(slot, st, depth + 1)?);
                    }
                    st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                    let mut steps: i32 = 0;
                    let mut flag = true;
                    for i in 0..ops.len() {
                        let text: &str = ops[i].as_ref();
                        let cop = cops[i];
                        let a = &operands[i];
                        let b = &operands[i + 1];
                        if text != "==" && text != "!=" && text != "in" && text != "not in" || true {
                            // "error forgot call" is enabled: functions are never valid operands
                            let f = match (a, b) {
                                (V::Func(f), _) => Some(f.clone()),
                                (_, V::Func(f)) => Some(f.clone()),
                                _ => None,
                            };
                            if let Some(f) = f {
                                return Err(Ctrl::Err(err("error_function_in_operator", &[f.name.to_string(), text.to_string()])));
                            }
                        }
                        let is_in = matches!(cop, COp::In | COp::NotIn);
                        if is_in && !(matches!(b, V::Dict(_) | V::Set(_)) || b.is_seq()) {
                            return Err(Ctrl::Err(err("error_bad_unary_operator", &[text.to_string(), nice_el(b)])));
                        }
                        let flag2 = match cop {
                            COp::Eq => py_equals(a, b, &mut steps)?,
                            COp::Ne => !py_equals(a, b, &mut steps)?,
                            COp::Ge => deep_compare(a, b, text, &mut steps)? >= 0,
                            COp::Le => deep_compare(a, b, text, &mut steps)? <= 0,
                            COp::Gt => deep_compare(a, b, text, &mut steps)? > 0,
                            COp::Lt => deep_compare(a, b, text, &mut steps)? < 0,
                            COp::In | COp::NotIn => {
                                let found = match b {
                                    V::Dict(d) | V::Set(d) => {
                                        let key = to_key(a)?;
                                        let r = d.borrow().contains(&key);
                                        steps += py_size(a);
                                        r
                                    }
                                    _ => seq_contains(b, a, &mut steps)?,
                                };
                                if cop == COp::In { found } else { !found }
                            }
                            // e.g. "not  in" written with extra spaces: the game leaves the result true
                            _ => true,
                        };
                        flag = flag && flag2;
                        if !flag {
                            break;
                        }
                    }
                    if check_inc(&st, OPERATION_OPS * steps as f64) {
                        yp(st);
                    }
                    Ok(V::Bool(flag))
                }
                NK::Branch(looping) => {
                    let looping = *looping;
                    eb(&st, &node, depth)?;
                    let mut first_loop = true;
                    let wait_name = if looping { busy_wait_name(&node) } else { None };
                    let items_spin = looping && wait_name.is_none() && is_items_spin(&node);
                    loop {
                        let condition;
                        if let Some(lit) = is_literal_node(&node.slots[0]) {
                            condition = is_true_value(&lit)?;
                        } else {
                            if let (Some(name), false) = (&wait_name, first_loop) {
                                let scope = st.borrow().current_scope();
                                let deadline = match scope_evaluate(&scope, name) {
                                    Ok((V::Num(n), _)) => Some(n),
                                    _ => None,
                                };
                                st.borrow_mut().wait_deadline = deadline;
                            }
                            if items_spin && !first_loop {
                                st.borrow_mut().spin_loop = true;
                            }
                            let cond_result = exec(&node.slots[0], st, depth + 1);
                            {
                                let mut s = st.borrow_mut();
                                s.wait_deadline = None;
                                s.spin_loop = false;
                            }
                            if cond_result.is_err() && items_spin {
                                let mut s = st.borrow_mut();
                                s.spin_read = None;
                                s.spin_period = None;
                            }
                            let cv = cond_result?;
                            condition = is_true_value(&cv)?;
                            if !condition && items_spin {
                                let mut s = st.borrow_mut();
                                s.spin_read = None;
                                s.spin_period = None;
                            }
                        }
                        if first_loop {
                            if check_inc(&st, OPERATION_OPS) {
                                yp(st);
                            }
                            first_loop = false;
                        }
                        if !condition {
                            break;
                        }
                        match exec_block(&node.slots[1], st, depth + 1) {
                            Ok(()) => {}
                            Err(Ctrl::Break) => {
                                if !looping {
                                    return Err(Ctrl::Break);
                                }
                                return Ok(V::None);
                            }
                            Err(Ctrl::Continue) => {
                                if !looping {
                                    return Err(Ctrl::Continue);
                                }
                            }
                            Err(e) => return Err(e),
                        }
                        if !looping {
                            return Ok(V::None);
                        }
                        eb(&st, &node, depth)?;
                        yp(st);
                    }
                    if node.slots.len() > 2 {
                        exec_block(&node.slots[2], st, depth + 1)?;
                    }
                    Ok(V::None)
                }
                NK::For => {
                    eb(&st, &node, depth)?;
                    let iterable = exec(&node.slots[0], st, depth + 1)?;
                    if !is_enumerable(&iterable) {
                        st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                        return Err(Ctrl::Err(err("error_for_requires_iterable", &[nice_el(&iterable)])));
                    }
                    let mut enumerator = PyIter::new(&iterable);
                    if check_inc(&st, OPERATION_OPS) {
                        yp(st);
                    }
                    let assign_op: Rc<str> = Rc::from("=");
                    loop {
                        let current = match enumerator.next()? {
                            Some(c) => c,
                            None => break,
                        };
                        assign(st, depth, &node.slots[2], current, &assign_op)?;
                        match exec_block(&node.slots[1], st, depth + 1) {
                            Ok(()) | Err(Ctrl::Continue) => {}
                            Err(Ctrl::Break) => return Ok(V::None),
                            Err(e) => return Err(e),
                        }
                        eb(&st, &node, depth)?;
                    }
                    Ok(V::None)
                }
                NK::Assignment(op) => {
                    eb(&st, &node, depth)?;
                    let value = exec(&node.slots[1], st, depth + 1)?;
                    st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                    assign(st, depth, &node.slots[0], value, &op)?;
                    Ok(V::None)
                }
                NK::Def(func_name, is_static) => {
                    eb(&st, &node, depth)?;
                    let scope = st.borrow().current_scope();
                    let f = Rc::new(PyFunc {
                        name: func_name.clone(),
                        syntax_tree: Some(node.slots[0].clone()),
                        parent_scope: Some(scope.clone()),
                        binding: None,
                        method_object: None,
                        is_free: false,
                    });
                    scope_set_var(&scope, func_name, V::Func(f), *is_static);
                    if check_inc(&st, OPERATION_OPS) {
                        yp(st);
                    }
                    Ok(V::None)
                }
                NK::Function { .. } => Err(Ctrl::Err("a function body cannot be executed without a call".into())),
                NK::Return => {
                    eb(&st, &node, depth)?;
                    let v = if !node.slots.is_empty() { exec(&node.slots[0], st, depth + 1)? } else { V::None };
                    stm(st).module_state.return_value = v;
                    if check_inc(&st, 0.0) {
                        yp(st);
                    }
                    st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                    Err(Ctrl::Return)
                }
                NK::Pass => {
                    eb(&st, &node, depth)?;
                    if check_inc(&st, OPERATION_OPS) {
                        yp(st);
                    }
                    Ok(V::None)
                }
                NK::Break => {
                    eb(&st, &node, depth)?;
                    if check_inc(&st, 0.0) {
                        yp(st);
                    }
                    Err(Ctrl::Break)
                }
                NK::Continue => {
                    eb(&st, &node, depth)?;
                    if check_inc(&st, 0.0) {
                        yp(st);
                    }
                    Err(Ctrl::Continue)
                }
                NK::Global => {
                    eb(&st, &node, depth)?;
                    yp(st);
                    Ok(V::None)
                }
                NK::Import { module_names, unpack, unpack_all, vars_to_unpack, is_static } => {
                    eb(&st, &node, depth)?;
                    if check_inc(&st, 0.0) {
                        yp(st);
                    }
                    for name in module_names.iter() {
                        let name: &str = name.as_ref();
                        if name == "__builtins__" || name == "builtins" {
                            continue;
                        }
                        let cached = st.borrow().module_cache.contains_key(name);
                        if !cached {
                            let path = st.borrow().sh.dir.join(format!("{}.py", name));
                            let code = match std::fs::read_to_string(&path) {
                                Ok(c) => c,
                                Err(_) => return Err(Ctrl::Err("error_module_not_found".into())),
                            };
                            let tree = match parse_source(name, &code) {
                                Ok(t) => t,
                                Err(e) => return Err(Ctrl::Err(format!("error_syntax_error_in_import: {}", e))),
                            };
                            let sh = st.borrow().sh.clone();
                            sh.trees.borrow_mut().push(tree.clone());
                            if let Err(e) = register_leaderboard_code(&sh, name, &tree) {
                                return Err(Ctrl::Err(e));
                            }
                            let scope = new_scope(None, None, &[]);
                            scope_import_var(&scope, &intern("__name__"), new_str(name), false);
                            let module = Rc::new(PyModule {
                                scope: scope.clone(),
                                name: name.to_string(),
                                fully_initialized: Cell::new(false),
                            });
                            st.borrow_mut().module_cache.insert(name.to_string(), module.clone());
                            register_builtins(&scope);
                            let module_state = ModuleState {
                                global_scope: scope,
                                call_stack: Vec::new(),
                                return_value: V::None,
                                is_expression_static: false,
                            };
                            let old = std::mem::replace(&mut st.borrow_mut().module_state, module_state);
                            let r = exec_block(&tree, st, depth);
                            st.borrow_mut().module_state = old;
                            r?;
                            module.fully_initialized.set(true);
                        }
                        let module = st.borrow().module_cache[name].clone();
                        let scope = st.borrow().current_scope();
                        if *unpack {
                            if *unpack_all {
                                let entries = module.scope.borrow().vars.entries();
                                for (k, v, s) in entries.iter() {
                                    if !k.starts_with('_') {
                                        scope_import_var(&scope, k, v.clone(), *s);
                                    }
                                }
                                continue;
                            }
                            for item in vars_to_unpack.iter() {
                                let (v, s) = module_export(&module, item)?;
                                scope_import_var(&scope, item, v, s);
                            }
                        } else {
                            scope_import_var(&scope, name, V::Module(module), *is_static);
                        }
                    }
                    Ok(V::None)
                }
                NK::List => {
                    eb(&st, &node, depth)?;
                    let elements = match exec(&node.slots[0], st, depth + 1)? {
                        V::Seq(s) => Rc::try_unwrap(s).unwrap_or_else(|s| s.to_vec()),
                        _ => Vec::new(),
                    };
                    let count = elements.len();
                    let value = new_list(elements);
                    set_static(&st, false);
                    if check_inc(&st, OPERATION_OPS * (count.max(1) as f64)) {
                        yp(st);
                    }
                    Ok(value)
                }
                NK::Tuple => {
                    eb(&st, &node, depth)?;
                    let elements = match exec(&node.slots[0], st, depth + 1)? {
                        V::Seq(s) => s,
                        _ => Rc::new(Vec::new()),
                    };
                    let value = V::Tuple(Rc::new(Rc::try_unwrap(elements).unwrap_or_else(|s| s.to_vec())));
                    set_static(&st, false);
                    if check_inc(&st, OPERATION_OPS) {
                        yp(st);
                    }
                    Ok(value)
                }
                NK::Dict => {
                    eb(&st, &node, depth)?;
                    let elements = match exec(&node.slots[0], st, depth + 1)? {
                        V::Seq(s) => s,
                        _ => Rc::new(Vec::new()),
                    };
                    let mut dictionary = DMap::new(false);
                    let mut i = 0;
                    while i < elements.len() {
                        let k = &elements[i];
                        if k.is_unhashable() {
                            st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                            return Err(Ctrl::Err(err("error_bad_key", &[nice_el(k)])));
                        }
                        dictionary.put(to_key(k)?, k.clone(), elements[i + 1].clone());
                        i += 2;
                    }
                    let count = dictionary.len();
                    let value = V::Dict(Rc::new(RefCell::new(dictionary)));
                    set_static(&st, false);
                    if check_inc(&st, OPERATION_OPS * (1 + count) as f64) {
                        yp(st);
                    }
                    Ok(value)
                }
                NK::Set => {
                    eb(&st, &node, depth)?;
                    let elements = match exec(&node.slots[0], st, depth + 1)? {
                        V::Seq(s) => s,
                        _ => Rc::new(Vec::new()),
                    };
                    let mut hash_set = DMap::new(true);
                    for k in elements.iter() {
                        if k.is_unhashable() {
                            st.borrow_mut().current_executing_node = Rc::as_ptr(node);
                            return Err(Ctrl::Err(err("error_bad_key", &[nice_el(k)])));
                        }
                        let key = to_key(k)?;
                        if !hash_set.contains(&key) {
                            hash_set.insert_new(key, k.clone(), V::None);
                        }
                    }
                    let value = V::Set(Rc::new(RefCell::new(hash_set)));
                    let size = py_size(&value);
                    set_static(&st, false);
                    if check_inc(&st, OPERATION_OPS * size.max(1) as f64) {
                        yp(st);
                    }
                    Ok(value)
                }
            }
        }
    }
}

/// PyModule.Export
fn module_export(m: &Rc<PyModule>, value: &str) -> R<(V, bool)> {
    match m.scope.borrow().vars.get(value) {
        Some(e) => Ok((e.1.clone(), e.2)),
        None => Err(err("error_invalid_const", &[format!("{}.{}", m.name, value)])),
    }
}

/// FunctionNode.Execute
fn exec_function(node: &Rc<Node>, st: &StRef, mut arguments: Vec<V>, depth: i32) -> Ev {
    {
        {
            let (param_names, func_name) = match &node.kind {
                NK::Function { params, name, .. } => (params, name),
                _ => return Err(Ctrl::Err("not a function".into())),
            };
            let num = param_names.len() as i32 - arguments.len() as i32;
            let num_default_values = node.slots.len() as i32 - 1;
            if num < 0 || num > num_default_values {
                return Err(Ctrl::Err(err(
                    "error_wrong_number_args",
                    &[func_name.to_string(), param_names.len().to_string(), nice_el(&V::Tuple(Rc::new(arguments.clone())))],
                )));
            }
            eb(&st, &node, depth)?;
            let mut i = num_default_values - num;
            while i < num_default_values {
                arguments.push(exec(&node.slots[(i + 1) as usize], st, depth + 1)?);
                i += 1;
            }
            {
                let scope = st.borrow().current_scope();
                for j in 0..param_names.len() {
                    scope_set_var(&scope, &param_names[j], arguments[j].clone(), false);
                }
            }
            match exec_block(&node.slots[0], st, depth + 1) {
                Ok(()) => {}
                Err(Ctrl::Break) => return Err(Ctrl::Err("error_no_loop_to_break".into())),
                Err(Ctrl::Continue) => return Err(Ctrl::Err("error_no_loop_to_continue".into())),
                Err(Ctrl::Return) => {
                    let s = stm(st);
                    s.module_state.call_stack.pop();
                    return Ok(std::mem::replace(&mut s.module_state.return_value, V::None));
                }
                Err(e) => return Err(e),
            }
            let s = stm(st);
            s.module_state.is_expression_static = false;
            s.module_state.call_stack.pop();
            Ok(V::None)
        }
    }
}

/// AssignmentNode.GetValueToAssign; returns (value, execTime)
fn get_value_to_assign(before: Option<&V>, rhs: &V, op: &str) -> R<(V, f64)> {
    if op == "=" {
        return Ok((rhs.clone(), 0.0));
    }
    let before = before.unwrap();
    if op == "+=" {
        if let (Some(a), Some(b)) = (before.num(), rhs.num()) {
            return Ok((V::Num(a + b), 1.0));
        }
        if let (V::List(l), true) = (before, is_enumerable(rhs)) {
            let items = enumerate(rhs);
            let n = items.len();
            l.borrow_mut().extend(items);
            return Ok((before.clone(), n as f64));
        }
        if let (V::Str(a), V::Str(b)) = (before, rhs) {
            let s = format!("{}{}", a, b);
            let n = s.chars().count();
            return Ok((new_str(&s), n as f64));
        }
        if let (V::Tuple(a), V::Tuple(b)) = (before, rhs) {
            let mut out = a.to_vec();
            out.extend(b.iter().cloned());
            let n = out.len();
            return Ok((V::Tuple(Rc::new(out)), n as f64));
        }
        return Err(err("error_bad_bin_operator", &[op.to_string(), nice_el(before), nice_el(rhs)]));
    }
    let (a, b) = match (before.num(), rhs.num()) {
        (Some(a), Some(b)) => (a, b),
        _ => return Err(err("error_arith_assign_not_used_on_number", &[op.to_string()])),
    };
    let v = match op {
        "-=" => a - b,
        "*=" => a * b,
        "/=" => a / b,
        "//=" => (a / b).floor(),
        "%=" => py_modulo(a, b),
        _ => return Err(err("error_arith_assign_not_used_on_number", &[op.to_string()])),
    };
    Ok((V::Num(v), 1.0))
}

/// AssignmentNode.Assign
fn assign(st: &StRef, depth: i32, lhs: &Rc<Node>, rhs: V, op: &Rc<str>) -> Res {
    {
        {
            match &lhs.kind {
                NK::Value(value) => {
                    let scope = st.borrow().current_scope();
                    let before = if op.as_ref() == "=" { None } else { Some(scope_evaluate(&scope, value)?.0) };
                    let (v, exec_time) = get_value_to_assign(before.as_ref(), &rhs, &op)?;
                    scope_set_var(&scope, value, v, false);
                    if check_inc(&st, OPERATION_OPS * exec_time) {
                        yp(st);
                    }
                    Ok(())
                }
                NK::Binary(bop, _, _) => {
                    let target = exec(&lhs.slots[0], st, depth + 1)?;
                    if bop.as_ref() == "." {
                        let module = match target {
                            V::Module(m) => m,
                            other => {
                                st.borrow_mut().current_executing_node = Rc::as_ptr(lhs);
                                return Err(Ctrl::Err(err("error_attribute_on_non_module", &[nice_el(&other)])));
                            }
                        };
                        let value2 = match &lhs.slots[1].kind {
                            NK::Value(v) => v.clone(),
                            _ => return Err(Ctrl::Err("error_invalid_const2".into())),
                        };
                        let num = if !st.borrow().module_state.is_expression_static { 1.0 } else { 0.0 };
                        let before = if op.as_ref() == "=" { None } else { Some(module_export(&module, &value2)?.0) };
                        let (v, exec_time) = get_value_to_assign(before.as_ref(), &rhs, &op)?;
                        module.scope.borrow_mut().vars.set(&value2, v, false);
                        if check_inc(&st, OPERATION_OPS * (exec_time + num)) {
                            yp(st);
                        }
                        return Ok(());
                    }
                    if bop.as_ref() == "[]" {
                        let indexable = target;
                        if !(indexable.is_seq() || matches!(indexable, V::Dict(_))) {
                            st.borrow_mut().current_executing_node = Rc::as_ptr(lhs);
                            return Err(Ctrl::Err(err("error_index_on_non_indexable", &[nice_el(&indexable)])));
                        }
                        let indices = match exec(&lhs.slots[1], st, depth + 1)? {
                            V::Seq(s) => s,
                            _ => Rc::new(Vec::new()),
                        };
                        let mut steps = 0;
                        let before =
                            if op.as_ref() == "=" { None } else { Some(index_at(&indexable, &indices, &mut steps, None)?) };
                        steps = 0;
                        let (v, exec_time) = get_value_to_assign(before.as_ref(), &rhs, &op)?;
                        index_at(&indexable, &indices, &mut steps, Some(v))?;
                        if check_inc(&st, OPERATION_OPS * (steps as f64 + exec_time)) {
                            yp(st);
                        }
                        return Ok(());
                    }
                    st.borrow_mut().current_executing_node = Rc::as_ptr(lhs);
                    Err(Ctrl::Err("error_assign_type_mismatch".into()))
                }
                NK::List | NK::Tuple => {
                    if !rhs.is_seq() {
                        return Err(Ctrl::Err("error_assign_type_mismatch".into()));
                    }
                    let left_nodes = &lhs.slots[0].slots;
                    let count = seq_len(&rhs);
                    if left_nodes.len() < count {
                        return Err(Ctrl::Err("error_too_many_values_to_unpack".into()));
                    }
                    if left_nodes.len() > count {
                        return Err(Ctrl::Err("error_not_enough_values".into()));
                    }
                    let right_values = seq_items(&rhs);
                    if matches!(rhs, V::List(_)) && check_inc(&st, OPERATION_OPS) {
                        yp(st);
                    }
                    for i in 0..left_nodes.len() {
                        assign(st, depth, &left_nodes[i], right_values[i].clone(), &op)?;
                    }
                    Ok(())
                }
                NK::Bracket => assign(st, depth, &lhs.slots[0], rhs.clone(), &op),
                _ => Err(Ctrl::Err("error_assign_type_mismatch".into())),
            }
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Bytecode: every syntax tree is compiled once into a flat list of instructions that perform the
// game's Node.Execute effects in the same order (ErrorsAndBreakpoints, op counts, yields, the
// static-expression flag, returnValue), and each drone's program is a small machine (Vm) that can
// stop after any instruction and carry on later. PerformExecutionStep runs it until the game's
// iterator would stop: past the target op count, a side effect, or 1000 resumes.
// ---------------------------------------------------------------------------------------------

#[derive(Clone, Copy)]
enum Op {
    /// ErrorsAndBreakpoints: the depth check and the error location
    Eb(*const Node, u32),
    SetNode(*const Node),
    /// Value: Eb, look the name up, set the static flag
    Load(*const Node, u32),
    /// Literal: Eb, push constant k, static flag off
    Lit(*const Node, u32, u32),
    MakeSeq(u32),
    Pop,
    PushNone,
    /// after the callee expression: it must be a function; push the static flag
    CallFunc(*const Node),
    /// Load of a plain name as the callee (Value node, depth) + CallFunc(call node)
    LoadCallee(*const Node, *const Node, u32),
    /// StoreName for an assignment straight to a name: sets the assignment node first (the
    /// SetNode it replaces); the operator comes from the assignment node
    StoreAssign(*const Node, *const Node),
    /// pops the arguments (this many, or one argument list for u32::MAX), the static flag and the
    /// function; a builtin is called here (then TakeRv, 3 on), a user function charges its op and
    /// goes on to CallB
    CallA(*const Node, u32),
    CallB,
    CallC,
    TakeRv,
    Unary(*const Node),
    /// and / or: short-circuits to the jump target with the left value
    AndOr(*const Node, bool, u32),
    AndOrRhs,
    /// `.` on a module or a constant bag: check_inc then CallDotFinish at the target
    DotMod(*const Node, u32),
    DotModFinish(*const Node),
    Bin(*const Node),
    Cmp(*const Node),
    MkList,
    MkTuple,
    MkDict(*const Node),
    MkSet(*const Node),
    Jump(u32),
    JumpIfFalse(u32),
    /// a literal condition: push its truth (no Eb, no ops)
    CondLit(u32),
    /// after a condition: clear the busy-wait markers, push its truth
    CondTest(bool),
    /// CondTest + ChargeFirst + JumpIfFalse(target) for a first pass; a JumpIfFalse(target) follows
    /// it, where the drone resumes if the charge stops it
    CondJumpF(bool, u32),
    /// CondTest + JumpIfFalse(else) + Jump(body) for a later pass of a loop
    LoopCond(bool, u32, u32),
    /// the first pass of a branch or loop costs one op
    ChargeFirst,
    /// before a later pass of `while get_time() < x` / `while num_items(...)`: set the markers
    WaitPre(*const Node, bool),
    Yp,
    /// pops the iterable, starts the iterator, one op
    ForInit(*const Node),
    /// next item, or pop the iterator and jump
    ForNext(u32),
    IterPop,
    /// assignment targets: each pops the value (and what it evaluated)
    StoreName(*const Node, u32),
    StoreAttr(*const Node, u32),
    IndexTarget(*const Node),
    StoreIndex(u32),
    Unpack(*const Node),
    Fail(u32),
    FailAt(*const Node, u32),
    Def(*const Node, u32),
    Pass(*const Node, u32),
    /// Break / Continue: Eb, check_inc(0), then go to the target
    BrkCont(*const Node, u32, u32),
    /// Return: store the value (popped), check_inc(0)
    RetA,
    RetB(*const Node),
    ImportStart(*const Node, u32),
    ImportLoad(*const Node, u32),
    ImportBind(*const Node, u32),
    /// function prologue
    ArgCheck(*const Node),
    Defaults(*const Node, u32),
    PushArg,
    BindParams(*const Node),
    FuncEnd,
    ModuleEnd,
}

struct Code {
    ops: Vec<Op>,
    consts: Vec<V>,
    strs: Vec<Rc<str>>,
    /// the tree this was compiled from (kept alive: instructions point into it)
    root: Rc<Node>,
}

/// error message ids used by Fail / FailAt
const FAIL_MSGS: &[&str] = &[
    "error_no_loop_to_break",
    "error_no_loop_to_continue",
    "error_assign_type_mismatch",
    "error_invalid_const2",
    "a function body cannot be executed without a call",
];

struct Compiler {
    ops: Vec<Op>,
    consts: Vec<V>,
    strs: Vec<Rc<str>>,
    /// innermost loop last: (break target fixups, continue target fixups)
    loops: Vec<(Vec<usize>, Vec<usize>)>,
    /// an Eb not yet emitted: dropped if the next instruction does its own Eb (see emit)
    pending_eb: Option<(*const Node, u32)>,
}

impl Compiler {
    fn here(&mut self) -> u32 {
        self.flush_eb();
        self.ops.len() as u32
    }
    fn flush_eb(&mut self) {
        if let Some((n, d)) = self.pending_eb.take() {
            self.ops.push(Op::Eb(n, d));
        }
    }
    fn eb(&mut self, n: *const Node, d: u32) {
        if let Some((pn, pd)) = self.pending_eb.take() {
            if pd >= 1000 {
                self.ops.push(Op::Eb(pn, pd));
            }
        }
        self.pending_eb = Some((n, d));
    }
    /// An Eb right before an instruction that starts with its own Eb (a child node's) is dropped:
    /// the child at once overwrites the error location, and its depth check (one deeper) fails
    /// whenever the parent's would, short of the 1100 limit the scripts come nowhere near.
    fn emit(&mut self, op: Op) -> usize {
        if let Some((n, d)) = self.pending_eb.take() {
            let starts_with_eb = matches!(op, Op::Load(..) | Op::Lit(..) | Op::Eb(..) | Op::Def(..) | Op::Pass(..) | Op::BrkCont(..) | Op::ImportStart(..) | Op::LoadCallee(..));
            if !(starts_with_eb && d < 1000) {
                self.ops.push(Op::Eb(n, d));
            }
        }
        self.ops.push(op);
        self.ops.len() - 1
    }
    fn patch(&mut self, at: usize, target: u32) {
        match &mut self.ops[at] {
            Op::Jump(t) | Op::JumpIfFalse(t) | Op::ForNext(t) | Op::AndOr(_, _, t) | Op::DotMod(_, t) | Op::BrkCont(_, _, t) | Op::CondJumpF(_, t) => *t = target,
            Op::LoopCond(_, t, _) => *t = target,
            _ => panic!("patch of a non-jump"),
        }
    }
    fn s(&mut self, v: &Rc<str>) -> u32 {
        self.strs.push(v.clone());
        (self.strs.len() - 1) as u32
    }

    /// statements: leave nothing on the stack
    fn block(&mut self, node: &Rc<Node>, depth: u32) {
        if let NK::Seq = &node.kind {
            for slot in node.slots.iter() {
                self.stmt(slot, depth + 1);
            }
        } else {
            self.stmt(node, depth);
        }
    }

    fn stmt(&mut self, node: &Rc<Node>, depth: u32) {
        let np = Rc::as_ptr(node);
        match &node.kind {
            NK::Seq => {
                for slot in node.slots.iter() {
                    self.stmt(slot, depth + 1);
                }
            }
            NK::Branch(looping) => self.branch(node, *looping, depth),
            NK::For => {
                self.eb(np, depth);
                self.expr(&node.slots[0], depth + 1);
                self.emit(Op::ForInit(np));
                let next = self.here();
                let fnext = self.emit(Op::ForNext(0));
                self.target(&node.slots[2], depth);
                self.loops.push((Vec::new(), Vec::new()));
                self.block(&node.slots[1], depth + 1);
                let (brks, conts) = self.loops.pop().unwrap();
                let tail = self.here();
                for c in conts {
                    self.patch(c, tail);
                }
                self.eb(np, depth);
                self.emit(Op::Jump(next));
                let brk = self.here();
                for b in brks {
                    self.patch(b, brk);
                }
                self.emit(Op::IterPop);
                let end = self.here();
                self.patch(fnext, end);
            }
            NK::Assignment(op) => {
                self.eb(np, depth);
                self.expr(&node.slots[1], depth + 1);
                if let NK::Value(_) = &node.slots[0].kind {
                    self.emit(Op::StoreAssign(np, Rc::as_ptr(&node.slots[0])));
                } else {
                    self.emit(Op::SetNode(np));
                    let k = self.s(op);
                    self.assign(&node.slots[0], depth, k);
                }
            }
            NK::Def(..) => {
                self.emit(Op::Def(np, depth));
            }
            NK::Return => {
                self.eb(np, depth);
                if !node.slots.is_empty() {
                    self.expr(&node.slots[0], depth + 1);
                } else {
                    self.emit(Op::PushNone);
                }
                self.emit(Op::RetA);
                self.emit(Op::RetB(np));
            }
            NK::Pass => {
                self.emit(Op::Pass(np, depth));
            }
            NK::Break | NK::Continue => {
                let is_break = matches!(&node.kind, NK::Break);
                if self.loops.is_empty() {
                    // no loop around it: Eb and check_inc(0) as usual, then the game's error
                    let at = self.emit(Op::BrkCont(np, depth, 0));
                    let t = self.here();
                    self.patch(at, t);
                    self.emit(Op::Fail(if is_break { 0 } else { 1 }));
                } else {
                    let at = self.emit(Op::BrkCont(np, depth, 0));
                    let l = self.loops.last_mut().unwrap();
                    if is_break {
                        l.0.push(at);
                    } else {
                        l.1.push(at);
                    }
                }
            }
            NK::Global => {
                self.eb(np, depth);
                self.emit(Op::Yp);
            }
            NK::Import { module_names, .. } => {
                self.emit(Op::ImportStart(np, depth));
                for i in 0..module_names.len() {
                    self.emit(Op::ImportLoad(np, i as u32));
                    self.emit(Op::ImportBind(np, i as u32));
                }
            }
            NK::Function { .. } => {
                self.emit(Op::Fail(4));
            }
            _ => {
                self.expr(node, depth);
                self.emit(Op::Pop);
            }
        }
    }

    fn branch(&mut self, node: &Rc<Node>, looping: bool, depth: u32) {
        let np = Rc::as_ptr(node);
        self.eb(np, depth);
        let wait_name = if looping { busy_wait_name(node) } else { None };
        let items_spin = looping && wait_name.is_none() && is_items_spin(node);
        let lit = is_literal_node(&node.slots[0]);
        let lit_k = lit.map(|v| {
            self.consts.push(v);
            (self.consts.len() - 1) as u32
        });
        // first pass
        let mut jf_first = Vec::new();
        match lit_k {
            Some(k) => {
                self.emit(Op::CondLit(k));
                self.emit(Op::ChargeFirst);
                jf_first.push(self.emit(Op::JumpIfFalse(0)));
            }
            None => {
                self.expr(&node.slots[0], depth + 1);
                jf_first.push(self.emit(Op::CondJumpF(items_spin, 0)));
                jf_first.push(self.emit(Op::JumpIfFalse(0)));
            }
        }
        let body = self.here();
        if looping {
            self.loops.push((Vec::new(), Vec::new()));
        }
        self.block(&node.slots[1], depth + 1);
        let mut jf_later = None;
        let mut to_end = Vec::new();
        if looping {
            let (brks, conts) = self.loops.pop().unwrap();
            let tail = self.here();
            for c in conts {
                self.patch(c, tail);
            }
            self.eb(np, depth);
            self.emit(Op::Yp);
            // later passes
            if lit_k.is_none() && (wait_name.is_some() || items_spin) {
                self.emit(Op::WaitPre(np, items_spin));
            }
            match lit_k {
                Some(k) => {
                    self.emit(Op::CondLit(k));
                    jf_later = Some(self.emit(Op::JumpIfFalse(0)));
                    self.emit(Op::Jump(body));
                }
                None => {
                    self.expr(&node.slots[0], depth + 1);
                    jf_later = Some(self.emit(Op::LoopCond(items_spin, 0, body)));
                }
            }
            to_end = brks;
        } else if node.slots.len() > 2 {
            to_end.push(self.emit(Op::Jump(0)));
        }
        let else_at = self.here();
        for j in jf_first {
            self.patch(j, else_at);
        }
        if let Some(j) = jf_later {
            self.patch(j, else_at);
        }
        if node.slots.len() > 2 {
            self.block(&node.slots[2], depth + 1);
        }
        let end = self.here();
        for j in to_end {
            self.patch(j, end);
        }
    }

    /// an assignment target; the value to store is on the stack
    fn target(&mut self, lhs: &Rc<Node>, depth: u32) {
        let k = {
            let eq: Rc<str> = Rc::from("=");
            self.s(&eq)
        };
        self.assign(lhs, depth, k);
    }

    fn assign(&mut self, lhs: &Rc<Node>, depth: u32, op: u32) {
        let lp = Rc::as_ptr(lhs);
        match &lhs.kind {
            NK::Value(_) => {
                self.emit(Op::StoreName(lp, op));
            }
            NK::Binary(bop, _, _) => {
                self.expr(&lhs.slots[0], depth + 1);
                if bop.as_ref() == "." {
                    self.emit(Op::StoreAttr(lp, op));
                } else if bop.as_ref() == "[]" {
                    self.emit(Op::IndexTarget(lp));
                    self.expr(&lhs.slots[1], depth + 1);
                    self.emit(Op::StoreIndex(op));
                } else {
                    self.emit(Op::FailAt(lp, 2));
                }
            }
            NK::List | NK::Tuple => {
                self.emit(Op::Unpack(lp));
                for el in lhs.slots[0].slots.iter() {
                    self.assign(el, depth, op);
                }
            }
            NK::Bracket => self.assign(&lhs.slots[0], depth, op),
            _ => {
                self.emit(Op::Fail(2));
            }
        }
    }

    /// expressions: leave exactly one value on the stack
    fn expr(&mut self, node: &Rc<Node>, depth: u32) {
        let np = Rc::as_ptr(node);
        match &node.kind {
            NK::Seq => {
                for slot in node.slots.iter() {
                    self.expr(slot, depth + 1);
                }
                self.emit(Op::MakeSeq(node.slots.len() as u32));
            }
            NK::Value(_) => {
                self.emit(Op::Load(np, depth));
            }
            NK::Literal(v) => {
                self.consts.push(v.clone());
                let k = (self.consts.len() - 1) as u32;
                self.emit(Op::Lit(np, depth, k));
            }
            NK::Bracket => self.expr(&node.slots[0], depth + 1),
            NK::Call => {
                self.eb(np, depth);
                if let NK::Value(_) = &node.slots[0].kind {
                    self.emit(Op::LoadCallee(Rc::as_ptr(&node.slots[0]), np, depth + 1));
                } else {
                    self.expr(&node.slots[0], depth + 1);
                    self.emit(Op::CallFunc(np));
                }
                let args = &node.slots[1];
                if let NK::Seq = &args.kind {
                    for slot in args.slots.iter() {
                        self.expr(slot, depth + 2);
                    }
                    self.emit(Op::CallA(np, args.slots.len() as u32));
                } else {
                    self.expr(args, depth + 1);
                    self.emit(Op::CallA(np, u32::MAX));
                }
                self.emit(Op::CallB);
                self.emit(Op::CallC);
                self.emit(Op::TakeRv);
            }
            NK::Unary(_) => {
                self.eb(np, depth);
                self.expr(&node.slots[0], depth + 1);
                self.emit(Op::Unary(np));
            }
            NK::Binary(_, _, bop) => {
                self.eb(np, depth);
                self.expr(&node.slots[0], depth + 1);
                match bop {
                    BOp::And | BOp::Or => {
                        let at = self.emit(Op::AndOr(np, *bop == BOp::And, 0));
                        self.expr(&node.slots[1], depth + 1);
                        self.emit(Op::SetNode(np));
                        self.emit(Op::AndOrRhs);
                        let end = self.here();
                        self.patch(at, end);
                    }
                    BOp::Dot => {
                        let at = self.emit(Op::DotMod(np, 0));
                        self.expr(&node.slots[1], depth + 1);
                        self.emit(Op::Bin(np));
                        let j = self.emit(Op::Jump(0));
                        let fin = self.here();
                        self.patch(at, fin);
                        self.emit(Op::DotModFinish(np));
                        let end = self.here();
                        self.patch(j, end);
                    }
                    _ => {
                        self.expr(&node.slots[1], depth + 1);
                        self.emit(Op::Bin(np));
                    }
                }
            }
            NK::Comparison(..) => {
                self.eb(np, depth);
                for slot in node.slots.iter() {
                    self.expr(slot, depth + 1);
                }
                self.emit(Op::Cmp(np));
            }
            NK::List | NK::Tuple | NK::Dict | NK::Set => {
                self.eb(np, depth);
                self.expr(&node.slots[0], depth + 1);
                self.emit(match &node.kind {
                    NK::List => Op::MkList,
                    NK::Tuple => Op::MkTuple,
                    NK::Dict => Op::MkDict(np),
                    _ => Op::MkSet(np),
                });
            }
            NK::Function { .. } => {
                self.emit(Op::Fail(4));
                self.emit(Op::PushNone);
            }
            // a statement where a value is wanted: run it, its value is None
            _ => {
                self.stmt(node, depth);
                self.emit(Op::PushNone);
            }
        }
    }
}

thread_local! {
    static CODES: RefCell<FxMap<usize, Rc<Code>>> = RefCell::new(FxMap::default());
}

/// The code of a module (its tree's statements) or of a function (its FunctionNode), compiled once
/// per thread. Trees live for the whole thread (parse_source keeps them), so a node's address names
/// it for good.
fn code_of(node: &Rc<Node>) -> Rc<Code> {
    let key = Rc::as_ptr(node) as usize;
    if let Some(c) = CODES.with(|c| c.borrow().get(&key).cloned()) {
        return c;
    }
    let mut c = Compiler { ops: Vec::new(), consts: Vec::new(), strs: Vec::new(), loops: Vec::new(), pending_eb: None };
    match &node.kind {
        NK::Function { .. } => {
            let np = Rc::as_ptr(node);
            c.emit(Op::ArgCheck(np));
            c.eb(np, 0);
            // default values: Defaults jumps to the first one still missing
            let ndef = node.slots.len() - 1;
            let d = c.emit(Op::Defaults(np, 0));
            let first = c.here();
            for i in 0..ndef {
                c.expr(&node.slots[i + 1], 1);
                c.emit(Op::PushArg);
            }
            let _ = (d, first);
            c.emit(Op::BindParams(np));
            c.block(&node.slots[0], 1);
            c.emit(Op::FuncEnd);
        }
        _ => {
            c.block(node, 0);
            c.emit(Op::ModuleEnd);
        }
    }
    c.flush_eb();
    let code = Rc::new(Code { ops: c.ops, consts: c.consts, strs: c.strs, root: node.clone() });
    CODES.with(|cs| cs.borrow_mut().insert(key, code.clone()));
    code
}

enum FrameKind {
    Main,
    Function,
    SpawnRoot,
    Module { module: Rc<PyModule>, old: ModuleState },
}

struct Frame {
    code: Rc<Code>,
    pc: usize,
    stack_base: usize,
    iter_base: usize,
    depth_off: u32,
    kind: FrameKind,
    args: Vec<V>,
}

struct Vm {
    frames: Vec<Frame>,
    stack: Vec<V>,
    iters: Vec<PyIter>,
    /// a user function call between CallA and CallC
    pending: Option<(Rc<PyFunc>, Vec<V>)>,
}

impl Vm {
    fn main(tree: &Rc<Node>) -> Vm {
        let code = code_of(tree);
        Vm {
            frames: vec![Frame { code, pc: 0, stack_base: 0, iter_base: 0, depth_off: 0, kind: FrameKind::Main, args: Vec::new() }],
            stack: Vec::new(),
            iters: Vec::new(),
            pending: None,
        }
    }
    fn spawned(fnode: &Rc<Node>, args: Vec<V>) -> Vm {
        let code = code_of(fnode);
        Vm {
            frames: vec![Frame { code, pc: 0, stack_base: 0, iter_base: 0, depth_off: 0, kind: FrameKind::SpawnRoot, args }],
            stack: Vec::new(),
            iters: Vec::new(),
            pending: None,
        }
    }
}

/// check_inc, then a yield point if it asks for one: true when the drone must stop here
#[inline(always)]
fn charge(st: &StRef, ops: f64) -> bool {
    check_inc(st, ops) && yield_stops(st)
}
/// a yield point: true when PerformExecutionStep stops here
#[inline(always)]
fn yield_stops(st: &StRef) -> bool {
    let s = stm(st);
    s.h().resumes += 1;
    !(s.h().op_count <= s.h().target_op_count) || s.has_side_effect() || s.h().resumes >= 1000
}

fn node_ref<'a>(p: *const Node) -> &'a Node {
    unsafe { &*p }
}

/// Runs the drone's program until it must stop (see yield_stops) or ends.
fn vm_run(st: &StRef, vm: &mut Vm) {
    let r = vm_loop(st, vm);
    match r {
        Ok(()) => {}
        Err(c) => {
            vm.frames.clear();
            program_finished(st, Err(c));
        }
    }
}

macro_rules! cur_scope {
    ($st:expr) => {{
        let s = stm($st);
        match s.module_state.call_stack.last() {
            Some(sc) => sc.clone(),
            None => s.module_state.global_scope.clone(),
        }
    }};
}

fn vm_loop(st: &StRef, vm: &mut Vm) -> Res {
    'frames: loop {
        let fi = vm.frames.len() - 1;
        let code = vm.frames[fi].code.clone();
        let depth_off = vm.frames[fi].depth_off;
        let mut pc = vm.frames[fi].pc;
        let ops = &code.ops;
        macro_rules! stop {
            ($next:expr) => {{
                vm.frames[fi].pc = $next;
                return Ok(());
            }};
        }
        macro_rules! eb {
            ($n:expr, $d:expr) => {{
                if $d + depth_off > 1100 {
                    return Err(Ctrl::Err("error_max_stack_size_reached".into()));
                }
                stm(st).current_executing_node = $n;
            }};
        }
        loop {
            let op = ops[pc];
            pc += 1;
            match op {
                Op::Eb(n, d) => eb!(n, d),
                Op::SetNode(n) => stm(st).current_executing_node = n,
                Op::Load(n, d) => {
                    eb!(n, d);
                    let node = node_ref(n);
                    let name = match &node.kind {
                        NK::Value(name) => name,
                        _ => unreachable!(),
                    };
                    let s = stm(st);
                    let scope = s.module_state.call_stack.last().unwrap_or(&s.module_state.global_scope);
                    let (v, is_static) = scope_lookup(scope, name, Some(&node.lookup))?;
                    s.module_state.is_expression_static = is_static;
                    vm.stack.push(v);
                }
                Op::Lit(n, d, k) => {
                    eb!(n, d);
                    stm(st).module_state.is_expression_static = false;
                    vm.stack.push(code.consts[k as usize].clone());
                }
                Op::MakeSeq(n) => {
                    let at = vm.stack.len() - n as usize;
                    let v: Vec<V> = vm.stack.drain(at..).collect();
                    vm.stack.push(V::Seq(Rc::new(v)));
                }
                Op::Pop => {
                    vm.stack.pop();
                }
                Op::PushNone => vm.stack.push(V::None),
                Op::LoadCallee(vn, cn, d) => {
                    eb!(vn, d);
                    let node = node_ref(vn);
                    let name = match &node.kind {
                        NK::Value(name) => name,
                        _ => unreachable!(),
                    };
                    let s = stm(st);
                    let scope = s.module_state.call_stack.last().unwrap_or(&s.module_state.global_scope);
                    let (v, is_static) = scope_lookup(scope, name, Some(&node.lookup))?;
                    s.module_state.is_expression_static = is_static;
                    if !matches!(v, V::Func(_)) {
                        s.current_executing_node = cn;
                        return Err(Ctrl::Err("error_not_a_function".into()));
                    }
                    vm.stack.push(v);
                    vm.stack.push(V::Bool(is_static));
                }
                Op::StoreAssign(an, ln) => {
                    stm(st).current_executing_node = an;
                    let rhs = vm.stack.pop().unwrap();
                    let value = match &node_ref(ln).kind {
                        NK::Value(v) => v,
                        _ => unreachable!(),
                    };
                    let op = match &node_ref(an).kind {
                        NK::Assignment(op) => op,
                        _ => unreachable!(),
                    };
                    let scope = cur_scope!(st);
                    let before = if op.as_ref() == "=" { None } else { Some(scope_evaluate(&scope, value)?.0) };
                    let (v, exec_time) = get_value_to_assign(before.as_ref(), &rhs, op)?;
                    scope_set_var(&scope, value, v, false);
                    if charge(st, OPERATION_OPS * exec_time) {
                        stop!(pc);
                    }
                }
                Op::CallFunc(n) => {
                    if !matches!(vm.stack.last(), Some(V::Func(_))) {
                        stm(st).current_executing_node = n;
                        return Err(Ctrl::Err("error_not_a_function".into()));
                    }
                    let is_static = stm(st).module_state.is_expression_static;
                    vm.stack.push(V::Bool(is_static));
                }
                Op::CallA(n, argc) => {
                    let args = if argc == u32::MAX {
                        vm.stack.pop().unwrap()
                    } else {
                        let at = vm.stack.len() - argc as usize;
                        V::Seq(Rc::new(vm.stack.drain(at..).collect()))
                    };
                    let is_static = matches!(vm.stack.pop(), Some(V::Bool(true)));
                    let func = match vm.stack.pop() {
                        Some(V::Func(f)) => f,
                        _ => unreachable!(),
                    };
                    // The builtin `tap` sets no result, so its call's value is the argument list
                    // left in returnValue; every other builtin sets one (directly or when its side
                    // effect is applied), so for them the list need not be kept.
                    let keep_args = func.syntax_tree.is_none() && func.binding == Some("tap");
                    let mut parameters: Vec<V> = match args {
                        V::Seq(s) if !keep_args => Rc::try_unwrap(s).unwrap_or_else(|s| s.to_vec()),
                        V::Seq(ref s) => s.to_vec(),
                        _ => Vec::new(),
                    };
                    let args = if keep_args { V::Seq(Rc::new(parameters.clone())) } else { V::None };
                    if let Some(m) = &func.method_object {
                        parameters.insert(0, m.clone());
                    }
                    stm(st).current_executing_node = n;
                    if func.syntax_tree.is_some() {
                        vm.pending = Some((func, parameters));
                        if charge(st, if is_static { 0.0 } else { OPERATION_OPS }) {
                            stop!(pc);
                        }
                    } else {
                        // A builtin's result arrives in returnValue: set by the builtin itself, or by
                        // the scheduler when it applies the side effect. One that sets none leaves the
                        // argument list there, as in the game.
                        stm(st).module_state.return_value = args;
                        let mut num = call_builtin(func.binding.unwrap(), parameters, st)?;
                        if func.is_free && !is_static {
                            num = num.max(OPERATION_OPS);
                        }
                        pc += 2;
                        if charge(st, num) {
                            stop!(pc);
                        }
                        // TakeRv
                        let v = std::mem::replace(&mut stm(st).module_state.return_value, V::None);
                        vm.stack.push(v);
                        pc += 1;
                    }
                }
                Op::CallB => {
                    let (func, parameters) = vm.pending.take().unwrap();
                    let tree = func.syntax_tree.clone().unwrap();
                    let vars: &[Rc<str>] = match &tree.kind {
                        NK::Function { vars, .. } => vars,
                        _ => &[],
                    };
                    let scope = new_scope(Some(tree.clone()), func.parent_scope.clone(), vars);
                    stm(st).module_state.call_stack.push(scope);
                    push_frame(st)?;
                    vm.pending = Some((func, parameters));
                    if yield_stops(st) {
                        stop!(pc);
                    }
                }
                Op::CallC => {
                    let (func, parameters) = vm.pending.take().unwrap();
                    let tree = func.syntax_tree.clone().unwrap();
                    vm.frames[fi].pc = pc + 1; // after TakeRv
                    let fcode = code_of(&tree);
                    vm.frames.push(Frame {
                        code: fcode,
                        pc: 0,
                        stack_base: vm.stack.len(),
                        iter_base: vm.iters.len(),
                        depth_off: 0,
                        kind: FrameKind::Function,
                        args: parameters,
                    });
                    continue 'frames;
                }
                Op::TakeRv => {
                    let v = std::mem::replace(&mut stm(st).module_state.return_value, V::None);
                    vm.stack.push(v);
                }
                Op::Unary(n) => {
                    stm(st).current_executing_node = n;
                    let value = vm.stack.pop().unwrap();
                    let op = match &node_ref(n).kind {
                        NK::Unary(op) => op,
                        _ => unreachable!(),
                    };
                    if let V::Func(f) = &value {
                        if op.as_ref() != "not" {
                            return Err(Ctrl::Err(err("error_function_in_operator", &[f.name.to_string(), op.to_string()])));
                        }
                    }
                    let r = match op.as_ref() {
                        "+" => {
                            if value.num().is_none() {
                                return Err(Ctrl::Err(err("error_bad_unary_operator", &[op.to_string(), nice_el(&value)])));
                            }
                            value
                        }
                        "-" => match value.num() {
                            Some(x) => V::Num(0.0 - x),
                            None => return Err(Ctrl::Err(err("error_bad_unary_operator", &[op.to_string(), nice_el(&value)]))),
                        },
                        _ => V::Bool(!is_true_value(&value)?),
                    };
                    vm.stack.push(r);
                }
                Op::AndOr(_, is_and, end) => {
                    let lhs = vm.stack.last().unwrap();
                    let t = is_true_value(lhs)?;
                    if (is_and && !t) || (!is_and && t) {
                        pc = end as usize;
                        if charge(st, OPERATION_OPS) {
                            stop!(pc);
                        }
                    } else {
                        vm.stack.pop();
                    }
                }
                Op::AndOrRhs => {
                    if charge(st, OPERATION_OPS) {
                        stop!(pc);
                    }
                }
                Op::DotMod(n, fin) => {
                    if matches!(vm.stack.last(), Some(V::Module(_) | V::Bag(_))) {
                        let node = node_ref(n);
                        if !matches!(&node.slots[1].kind, NK::Value(_)) {
                            return Err(Ctrl::Err("error_invalid_const2".into()));
                        }
                        let is_static = stm(st).module_state.is_expression_static;
                        pc = fin as usize;
                        if charge(st, if is_static { 0.0 } else { OPERATION_OPS }) {
                            stop!(pc);
                        }
                    }
                }
                Op::DotModFinish(n) => {
                    let lhs = vm.stack.pop().unwrap();
                    let node = node_ref(n);
                    let member = match &node.slots[1].kind {
                        NK::Value(v) => v,
                        _ => unreachable!(),
                    };
                    let (v, flag) = match &lhs {
                        V::Module(m) => module_export(m, member)?,
                        V::Bag(ns) => (bag_evaluate(*ns, member)?, true),
                        _ => unreachable!(),
                    };
                    stm(st).module_state.is_expression_static &= flag;
                    vm.stack.push(v);
                }
                Op::Bin(n) => {
                    stm(st).current_executing_node = n;
                    let rhs = vm.stack.pop().unwrap();
                    let lhs = vm.stack.pop().unwrap();
                    let (op, bop) = match &node_ref(n).kind {
                        NK::Binary(op, _, bop) => (op.as_ref(), *bop),
                        _ => unreachable!(),
                    };
                    let (result, steps) = binary_value(op, bop, lhs, rhs)?;
                    vm.stack.push(result);
                    if charge(st, OPERATION_OPS * steps as f64) {
                        stop!(pc);
                    }
                }
                Op::Cmp(n) => {
                    stm(st).current_executing_node = n;
                    let node = node_ref(n);
                    let (ops_t, cops) = match &node.kind {
                        NK::Comparison(o, c) => (o, c),
                        _ => unreachable!(),
                    };
                    let at = vm.stack.len() - node.slots.len();
                    let (flag, steps) = compare_values(ops_t, cops, &vm.stack[at..])?;
                    vm.stack.truncate(at);
                    vm.stack.push(V::Bool(flag));
                    if charge(st, OPERATION_OPS * steps as f64) {
                        stop!(pc);
                    }
                }
                Op::MkList => {
                    let elements = match vm.stack.pop().unwrap() {
                        V::Seq(s) => Rc::try_unwrap(s).unwrap_or_else(|s| s.to_vec()),
                        _ => Vec::new(),
                    };
                    let count = elements.len();
                    vm.stack.push(new_list(elements));
                    set_static(st, false);
                    if charge(st, OPERATION_OPS * (count.max(1) as f64)) {
                        stop!(pc);
                    }
                }
                Op::MkTuple => {
                    let elements = match vm.stack.pop().unwrap() {
                        V::Seq(s) => Rc::try_unwrap(s).unwrap_or_else(|s| s.to_vec()),
                        _ => Vec::new(),
                    };
                    vm.stack.push(V::Tuple(Rc::new(elements)));
                    set_static(st, false);
                    if charge(st, OPERATION_OPS) {
                        stop!(pc);
                    }
                }
                Op::MkDict(n) => {
                    let elements = match vm.stack.pop().unwrap() {
                        V::Seq(s) => s,
                        _ => Rc::new(Vec::new()),
                    };
                    let mut dictionary = DMap::new(false);
                    let mut i = 0;
                    while i < elements.len() {
                        let k = &elements[i];
                        if k.is_unhashable() {
                            stm(st).current_executing_node = n;
                            return Err(Ctrl::Err(err("error_bad_key", &[nice_el(k)])));
                        }
                        dictionary.put(to_key(k)?, k.clone(), elements[i + 1].clone());
                        i += 2;
                    }
                    let count = dictionary.len();
                    vm.stack.push(V::Dict(Rc::new(RefCell::new(dictionary))));
                    set_static(st, false);
                    if charge(st, OPERATION_OPS * (1 + count) as f64) {
                        stop!(pc);
                    }
                }
                Op::MkSet(n) => {
                    let elements = match vm.stack.pop().unwrap() {
                        V::Seq(s) => s,
                        _ => Rc::new(Vec::new()),
                    };
                    let mut hash_set = DMap::new(true);
                    for k in elements.iter() {
                        if k.is_unhashable() {
                            stm(st).current_executing_node = n;
                            return Err(Ctrl::Err(err("error_bad_key", &[nice_el(k)])));
                        }
                        let key = to_key(k)?;
                        if !hash_set.contains(&key) {
                            hash_set.insert_new(key, k.clone(), V::None);
                        }
                    }
                    let value = V::Set(Rc::new(RefCell::new(hash_set)));
                    let size = py_size(&value);
                    vm.stack.push(value);
                    set_static(st, false);
                    if charge(st, OPERATION_OPS * size.max(1) as f64) {
                        stop!(pc);
                    }
                }
                Op::Jump(t) => pc = t as usize,
                Op::JumpIfFalse(t) => {
                    if matches!(vm.stack.pop(), Some(V::Bool(false))) {
                        pc = t as usize;
                    }
                }
                Op::CondLit(k) => {
                    let c = is_true_value(&code.consts[k as usize])?;
                    vm.stack.push(V::Bool(c));
                }
                Op::CondTest(items_spin) => {
                    let cv = vm.stack.pop().unwrap();
                    {
                        let s = stm(st);
                        s.wait_deadline = None;
                        s.spin_loop = false;
                    }
                    let condition = is_true_value(&cv)?;
                    if !condition && items_spin {
                        let s = stm(st);
                        s.spin_read = None;
                        s.spin_period = None;
                    }
                    vm.stack.push(V::Bool(condition));
                }
                Op::CondJumpF(items_spin, t) => {
                    let cv = vm.stack.pop().unwrap();
                    let condition = cond_truth(st, &cv, items_spin)?;
                    // ChargeFirst; if it stops, the JumpIfFalse after this decides on resume
                    if charge(st, OPERATION_OPS) {
                        vm.stack.push(V::Bool(condition));
                        stop!(pc);
                    }
                    pc = if condition { pc + 1 } else { t as usize };
                }
                Op::LoopCond(items_spin, e, b) => {
                    let cv = vm.stack.pop().unwrap();
                    let condition = cond_truth(st, &cv, items_spin)?;
                    pc = if condition { b as usize } else { e as usize };
                }
                Op::ChargeFirst => {
                    if charge(st, OPERATION_OPS) {
                        stop!(pc);
                    }
                }
                Op::WaitPre(n, items_spin) => {
                    let node = node_ref(n);
                    if !items_spin {
                        if let Some(name) = busy_wait_name_ref(node) {
                            let scope = cur_scope!(st);
                            let deadline = match scope_evaluate(&scope, name) {
                                Ok((V::Num(x), _)) => Some(x),
                                _ => None,
                            };
                            stm(st).wait_deadline = deadline;
                        }
                    } else {
                        stm(st).spin_loop = true;
                    }
                }
                Op::Yp => {
                    if yield_stops(st) {
                        stop!(pc);
                    }
                }
                Op::ForInit(n) => {
                    let iterable = vm.stack.pop().unwrap();
                    if !is_enumerable(&iterable) {
                        stm(st).current_executing_node = n;
                        return Err(Ctrl::Err(err("error_for_requires_iterable", &[nice_el(&iterable)])));
                    }
                    vm.iters.push(PyIter::new(&iterable));
                    if charge(st, OPERATION_OPS) {
                        stop!(pc);
                    }
                }
                Op::ForNext(end) => match vm.iters.last_mut().unwrap().next()? {
                    Some(c) => vm.stack.push(c),
                    None => {
                        vm.iters.pop();
                        pc = end as usize;
                    }
                },
                Op::IterPop => {
                    vm.iters.pop();
                }
                Op::StoreName(n, k) => {
                    let rhs = vm.stack.pop().unwrap();
                    let value = match &node_ref(n).kind {
                        NK::Value(v) => v,
                        _ => unreachable!(),
                    };
                    let op = &code.strs[k as usize];
                    let scope = cur_scope!(st);
                    let before = if op.as_ref() == "=" { None } else { Some(scope_evaluate(&scope, value)?.0) };
                    let (v, exec_time) = get_value_to_assign(before.as_ref(), &rhs, op)?;
                    scope_set_var(&scope, value, v, false);
                    if charge(st, OPERATION_OPS * exec_time) {
                        stop!(pc);
                    }
                }
                Op::StoreAttr(n, k) => {
                    let target = vm.stack.pop().unwrap();
                    let rhs = vm.stack.pop().unwrap();
                    let lhs = node_ref(n);
                    let op = &code.strs[k as usize];
                    let module = match target {
                        V::Module(m) => m,
                        other => {
                            stm(st).current_executing_node = n;
                            return Err(Ctrl::Err(err("error_attribute_on_non_module", &[nice_el(&other)])));
                        }
                    };
                    let value2 = match &lhs.slots[1].kind {
                        NK::Value(v) => v.clone(),
                        _ => return Err(Ctrl::Err("error_invalid_const2".into())),
                    };
                    let num = if !stm(st).module_state.is_expression_static { 1.0 } else { 0.0 };
                    let before = if op.as_ref() == "=" { None } else { Some(module_export(&module, &value2)?.0) };
                    let (v, exec_time) = get_value_to_assign(before.as_ref(), &rhs, op)?;
                    module.scope.borrow_mut().vars.set(&value2, v, false);
                    if charge(st, OPERATION_OPS * (exec_time + num)) {
                        stop!(pc);
                    }
                }
                Op::IndexTarget(n) => {
                    let t = vm.stack.last().unwrap();
                    if !(t.is_seq() || matches!(t, V::Dict(_))) {
                        stm(st).current_executing_node = n;
                        return Err(Ctrl::Err(err("error_index_on_non_indexable", &[nice_el(t)])));
                    }
                }
                Op::StoreIndex(k) => {
                    let indices = match vm.stack.pop().unwrap() {
                        V::Seq(s) => s,
                        _ => Rc::new(Vec::new()),
                    };
                    let indexable = vm.stack.pop().unwrap();
                    let rhs = vm.stack.pop().unwrap();
                    let op = &code.strs[k as usize];
                    let mut steps = 0;
                    let before = if op.as_ref() == "=" { None } else { Some(index_at(&indexable, &indices, &mut steps, None)?) };
                    steps = 0;
                    let (v, exec_time) = get_value_to_assign(before.as_ref(), &rhs, op)?;
                    index_at(&indexable, &indices, &mut steps, Some(v))?;
                    if charge(st, OPERATION_OPS * (steps as f64 + exec_time)) {
                        stop!(pc);
                    }
                }
                Op::Unpack(n) => {
                    let rhs = vm.stack.pop().unwrap();
                    if !rhs.is_seq() {
                        return Err(Ctrl::Err("error_assign_type_mismatch".into()));
                    }
                    let left = node_ref(n).slots[0].slots.len();
                    let count = seq_len(&rhs);
                    if left < count {
                        return Err(Ctrl::Err("error_too_many_values_to_unpack".into()));
                    }
                    if left > count {
                        return Err(Ctrl::Err("error_not_enough_values".into()));
                    }
                    let right_values = seq_items(&rhs);
                    for v in right_values.into_iter().rev() {
                        vm.stack.push(v);
                    }
                    if matches!(rhs, V::List(_)) && charge(st, OPERATION_OPS) {
                        stop!(pc);
                    }
                }
                Op::Fail(m) => return Err(Ctrl::Err(FAIL_MSGS[m as usize].into())),
                Op::FailAt(n, m) => {
                    stm(st).current_executing_node = n;
                    return Err(Ctrl::Err(FAIL_MSGS[m as usize].into()));
                }
                Op::Def(n, d) => {
                    eb!(n, d);
                    let node = node_ref(n);
                    let (func_name, is_static) = match &node.kind {
                        NK::Def(f, s) => (f, *s),
                        _ => unreachable!(),
                    };
                    let scope = cur_scope!(st);
                    let f = Rc::new(PyFunc {
                        name: func_name.clone(),
                        syntax_tree: Some(node.slots[0].clone()),
                        parent_scope: Some(scope.clone()),
                        binding: None,
                        method_object: None,
                        is_free: false,
                    });
                    scope_set_var(&scope, func_name, V::Func(f), is_static);
                    if charge(st, OPERATION_OPS) {
                        stop!(pc);
                    }
                }
                Op::Pass(n, d) => {
                    eb!(n, d);
                    if charge(st, OPERATION_OPS) {
                        stop!(pc);
                    }
                }
                Op::BrkCont(n, d, t) => {
                    eb!(n, d);
                    pc = t as usize;
                    if charge(st, 0.0) {
                        stop!(pc);
                    }
                }
                Op::RetA => {
                    let v = vm.stack.pop().unwrap();
                    stm(st).module_state.return_value = v;
                    if charge(st, 0.0) {
                        stop!(pc);
                    }
                }
                Op::RetB(n) => {
                    stm(st).current_executing_node = n;
                    // return from the innermost function frame
                    loop {
                        let f = vm.frames.last().unwrap();
                        match f.kind {
                            FrameKind::Function | FrameKind::SpawnRoot => break,
                            FrameKind::Main => return Err(Ctrl::Return),
                            FrameKind::Module { .. } => return Err(Ctrl::Return),
                        }
                    }
                    let f = vm.frames.pop().unwrap();
                    vm.stack.truncate(f.stack_base);
                    vm.iters.truncate(f.iter_base);
                    let s = stm(st);
                    s.module_state.call_stack.pop();
                    let v = std::mem::replace(&mut s.module_state.return_value, V::None);
                    match f.kind {
                        FrameKind::SpawnRoot => {
                            s.module_state.return_value = v;
                            program_finished(st, Ok(()));
                            return Ok(());
                        }
                        _ => {
                            s.frames -= 1;
                            vm.stack.push(v);
                            continue 'frames;
                        }
                    }
                }
                Op::ImportStart(n, d) => {
                    eb!(n, d);
                    if charge(st, 0.0) {
                        stop!(pc);
                    }
                }
                Op::ImportLoad(n, i) => {
                    let node = node_ref(n);
                    let name: &str = match &node.kind {
                        NK::Import { module_names, .. } => module_names[i as usize].as_ref(),
                        _ => unreachable!(),
                    };
                    if name == "__builtins__" || name == "builtins" {
                        continue;
                    }
                    let cached = stm(st).module_cache.contains_key(name);
                    if !cached {
                        let path = stm(st).sh.dir.join(format!("{}.py", name));
                        let code_text = match std::fs::read_to_string(&path) {
                            Ok(c) => c,
                            Err(_) => return Err(Ctrl::Err("error_module_not_found".into())),
                        };
                        let tree = match parse_source(name, &code_text) {
                            Ok(t) => t,
                            Err(e) => return Err(Ctrl::Err(format!("error_syntax_error_in_import: {}", e))),
                        };
                        let sh = stm(st).sh.clone();
                        sh.trees.borrow_mut().push(tree.clone());
                        if let Err(e) = register_leaderboard_code(&sh, name, &tree) {
                            return Err(Ctrl::Err(e));
                        }
                        let scope = new_scope(None, None, &[]);
                        scope_import_var(&scope, &intern("__name__"), new_str(name), false);
                        let module = Rc::new(PyModule { scope: scope.clone(), name: name.to_string(), fully_initialized: Cell::new(false) });
                        stm(st).module_cache.insert(name.to_string(), module.clone());
                        register_builtins(&scope);
                        let module_state = ModuleState { global_scope: scope, call_stack: Vec::new(), return_value: V::None, is_expression_static: false };
                        let old = std::mem::replace(&mut stm(st).module_state, module_state);
                        // the module's statements run at the import's depth
                        let d = depth_off + import_depth(&code.ops, pc - 1);
                        vm.frames[fi].pc = pc;
                        let mcode = code_of(&tree);
                        vm.frames.push(Frame {
                            code: mcode,
                            pc: 0,
                            stack_base: vm.stack.len(),
                            iter_base: vm.iters.len(),
                            depth_off: d,
                            kind: FrameKind::Module { module, old },
                            args: Vec::new(),
                        });
                        continue 'frames;
                    }
                }
                Op::ImportBind(n, i) => {
                    let node = node_ref(n);
                    let (name, unpack, unpack_all, vars_to_unpack, is_static) = match &node.kind {
                        NK::Import { module_names, unpack, unpack_all, vars_to_unpack, is_static } => {
                            (module_names[i as usize].as_ref(), *unpack, *unpack_all, vars_to_unpack, *is_static)
                        }
                        _ => unreachable!(),
                    };
                    if name == "__builtins__" || name == "builtins" {
                        continue;
                    }
                    let module = stm(st).module_cache[name].clone();
                    let scope = cur_scope!(st);
                    if unpack {
                        if unpack_all {
                            let entries = module.scope.borrow().vars.entries();
                            for (k, v, s) in entries.iter() {
                                if !k.starts_with('_') {
                                    scope_import_var(&scope, k, v.clone(), *s);
                                }
                            }
                            continue;
                        }
                        for item in vars_to_unpack.iter() {
                            let (v, s) = module_export(&module, item)?;
                            scope_import_var(&scope, item, v, s);
                        }
                    } else {
                        scope_import_var(&scope, name, V::Module(module), is_static);
                    }
                }
                Op::ArgCheck(n) => {
                    let node = node_ref(n);
                    let (param_names, func_name) = match &node.kind {
                        NK::Function { params, name, .. } => (params, name),
                        _ => unreachable!(),
                    };
                    let arguments = &vm.frames[fi].args;
                    let num = param_names.len() as i32 - arguments.len() as i32;
                    let num_default_values = node.slots.len() as i32 - 1;
                    if num < 0 || num > num_default_values {
                        return Err(Ctrl::Err(err(
                            "error_wrong_number_args",
                            &[func_name.to_string(), param_names.len().to_string(), nice_el(&V::Tuple(Rc::new(arguments.clone())))],
                        )));
                    }
                }
                Op::Defaults(n, _) => {
                    // skip the default values the call gave arguments for
                    let node = node_ref(n);
                    let nparams = match &node.kind {
                        NK::Function { params, .. } => params.len(),
                        _ => unreachable!(),
                    };
                    let ndef = node.slots.len() - 1;
                    let missing = nparams - vm.frames[fi].args.len();
                    let skip = ndef - missing;
                    // each default is its code followed by PushArg; walk past `skip` of them
                    let mut k = 0;
                    while k < skip {
                        if let Op::PushArg = ops[pc] {
                            k += 1;
                        }
                        pc += 1;
                    }
                }
                Op::PushArg => {
                    let v = vm.stack.pop().unwrap();
                    vm.frames[fi].args.push(v);
                }
                Op::BindParams(n) => {
                    let node = node_ref(n);
                    let param_names = match &node.kind {
                        NK::Function { params, .. } => params,
                        _ => unreachable!(),
                    };
                    let scope = cur_scope!(st);
                    let args = std::mem::take(&mut vm.frames[fi].args);
                    for (j, a) in args.into_iter().enumerate().take(param_names.len()) {
                        scope_set_var(&scope, &param_names[j], a, false);
                    }
                }
                Op::FuncEnd => {
                    let f = vm.frames.pop().unwrap();
                    vm.stack.truncate(f.stack_base);
                    vm.iters.truncate(f.iter_base);
                    let s = stm(st);
                    s.module_state.is_expression_static = false;
                    s.module_state.call_stack.pop();
                    match f.kind {
                        FrameKind::SpawnRoot => {
                            s.module_state.return_value = V::None;
                            program_finished(st, Ok(()));
                            return Ok(());
                        }
                        _ => {
                            s.frames -= 1;
                            vm.stack.push(V::None);
                            continue 'frames;
                        }
                    }
                }
                Op::ModuleEnd => {
                    let f = vm.frames.pop().unwrap();
                    match f.kind {
                        FrameKind::Module { module, old } => {
                            stm(st).module_state = old;
                            module.fully_initialized.set(true);
                            continue 'frames;
                        }
                        _ => {
                            program_finished(st, Ok(()));
                            return Ok(());
                        }
                    }
                }
            }
        }
    }
}

/// CondTest's work: clear the busy-wait markers, then the condition's truth.
#[inline(always)]
fn cond_truth(st: &StRef, cv: &V, items_spin: bool) -> R<bool> {
    let s = stm(st);
    s.wait_deadline = None;
    s.spin_loop = false;
    let condition = is_true_value(cv)?;
    if !condition && items_spin {
        s.spin_read = None;
        s.spin_period = None;
    }
    Ok(condition)
}

/// the static depth of the ImportStart before an ImportLoad at `at`
fn import_depth(ops: &[Op], at: usize) -> u32 {
    let mut i = at;
    loop {
        if let Op::ImportStart(_, d) = ops[i] {
            return d;
        }
        i -= 1;
    }
}

fn busy_wait_name_ref(node: &Node) -> Option<&Rc<str>> {
    let cond = &node.slots[0];
    match &cond.slots.get(1).map(|n| &n.kind) {
        Some(NK::Value(name)) => Some(name),
        _ => None,
    }
}

/// BinaryNode.Execute's operator part, for everything but and / or / module access: the value
/// and the steps it costs.
fn binary_value(op: &str, bop: BOp, lhs: V, rhs: V) -> R<(V, i32)> {
    if !matches!(bop, BOp::And | BOp::Or | BOp::Dot) {
        let f = match (&lhs, &rhs) {
            (V::Func(f), _) => Some(f.clone()),
            (_, V::Func(f)) => Some(f.clone()),
            _ => None,
        };
        if let Some(f) = f {
            return Err(err("error_function_in_operator", &[f.name.to_string(), op.to_string()]));
        }
    }
    if let (BOp::Sub | BOp::Mul | BOp::Div | BOp::FloorDiv | BOp::Mod | BOp::Pow | BOp::Add, V::Num(a), V::Num(b)) = (bop, &lhs, &rhs) {
        let (a, b) = (*a, *b);
        if matches!(bop, BOp::Div | BOp::FloorDiv | BOp::Mod) && b == 0.0 {
            return Err("error_division_by_zero".into());
        }
        return Ok((
            V::Num(match bop {
                BOp::Add => a + b,
                BOp::Sub => a - b,
                BOp::Mul => a * b,
                BOp::Div => a / b,
                BOp::FloorDiv => (a / b).floor(),
                BOp::Mod => py_modulo(a, b),
                _ => a.powf(b),
            }),
            1,
        ));
    }
    let bad = || err("error_bad_bin_operator", &[op.to_string(), nice_el(&lhs), nice_el(&rhs)]);
    let mut steps: i32 = 0;
    let result: V = match bop {
        BOp::And | BOp::Or => {
            steps = 1;
            rhs.clone()
        }
        BOp::Index => {
            if !(lhs.is_seq() || matches!(lhs, V::Dict(_))) {
                return Err(err("error_index_on_non_indexable", &[nice_el(&lhs)]));
            }
            let indices = match &rhs {
                V::Seq(s) => s.clone(),
                _ => Rc::new(Vec::new()),
            };
            index_at(&lhs, &indices, &mut steps, None)?
        }
        BOp::Add => {
            if let (Some(a), Some(b)) = (lhs.num(), rhs.num()) {
                steps = 1;
                V::Num(a + b)
            } else if let (V::List(a), true) = (&lhs, rhs.is_seq()) {
                let mut out = a.borrow().clone();
                out.extend(seq_items(&rhs));
                steps = (out.len() as i32).max(1);
                new_list(out)
            } else if let (V::Tuple(a), V::Tuple(b)) = (&lhs, &rhs) {
                let mut out = a.to_vec();
                out.extend(b.iter().cloned());
                steps = (out.len() as i32).max(1);
                V::Tuple(Rc::new(out))
            } else if let (V::Str(a), V::Str(b)) = (&lhs, &rhs) {
                steps = ((a.chars().count() + b.chars().count()) as i32).max(1);
                new_str(&format!("{}{}", a, b))
            } else {
                return Err(bad());
            }
        }
        BOp::Dot => match &rhs {
            V::Func(f) => {
                steps = 0;
                V::Func(Rc::new(PyFunc {
                    name: f.name.clone(),
                    syntax_tree: f.syntax_tree.clone(),
                    parent_scope: f.parent_scope.clone(),
                    binding: f.binding,
                    method_object: Some(lhs.clone()),
                    is_free: f.is_free,
                }))
            }
            _ => return Err("error_unknown_method".into()),
        },
        _ => {
            if matches!(bop, BOp::Div | BOp::FloorDiv | BOp::Mod) && rhs.num() == Some(0.0) {
                return Err("error_division_by_zero".into());
            }
            let (a, b) = match (lhs.num(), rhs.num()) {
                (Some(a), Some(b)) => (a, b),
                _ => return Err(bad()),
            };
            steps = 1;
            V::Num(match bop {
                BOp::Sub => a - b,
                BOp::Mul => a * b,
                BOp::Div => a / b,
                BOp::FloorDiv => (a / b).floor(),
                BOp::Mod => py_modulo(a, b),
                BOp::Pow => a.powf(b),
                _ => return Err(bad()),
            })
        }
    };
    Ok((result, steps))
}

/// ComparisonNode.Execute's operator part: the result and the steps it costs.
fn compare_values(ops: &[Rc<str>], cops: &[COp], operands: &[V]) -> R<(bool, i32)> {
    let mut steps: i32 = 0;
    let mut flag = true;
    for i in 0..ops.len() {
        let text: &str = ops[i].as_ref();
        let cop = cops[i];
        let a = &operands[i];
        let b = &operands[i + 1];
        let f = match (a, b) {
            (V::Func(f), _) => Some(f.clone()),
            (_, V::Func(f)) => Some(f.clone()),
            _ => None,
        };
        if let Some(f) = f {
            return Err(err("error_function_in_operator", &[f.name.to_string(), text.to_string()]));
        }
        let is_in = matches!(cop, COp::In | COp::NotIn);
        if is_in && !(matches!(b, V::Dict(_) | V::Set(_)) || b.is_seq()) {
            return Err(err("error_bad_unary_operator", &[text.to_string(), nice_el(b)]));
        }
        let flag2 = match cop {
            COp::Eq => py_equals(a, b, &mut steps)?,
            COp::Ne => !py_equals(a, b, &mut steps)?,
            COp::Ge => deep_compare(a, b, text, &mut steps)? >= 0,
            COp::Le => deep_compare(a, b, text, &mut steps)? <= 0,
            COp::Gt => deep_compare(a, b, text, &mut steps)? > 0,
            COp::Lt => deep_compare(a, b, text, &mut steps)? < 0,
            COp::In | COp::NotIn => {
                let found = match b {
                    V::Dict(d) | V::Set(d) => {
                        let key = to_key(a)?;
                        let r = d.borrow().contains(&key);
                        steps += py_size(a);
                        r
                    }
                    _ => seq_contains(b, a, &mut steps)?,
                };
                if cop == COp::In { found } else { !found }
            }
            _ => true,
        };
        flag = flag && flag2;
        if !flag {
            break;
        }
    }
    Ok((flag, steps))
}

// ---------------------------------------------------------------------------------------------
// BuiltinFunctions: each returns the ops it costs right away; world access is deferred by
// setting currentSideEffect, which Execution.ApplySideEffect performs when it is this drone's turn.
// ---------------------------------------------------------------------------------------------
fn wrong_args(i: usize, function: &str, v: &V) -> String {
    err("error_wrong_args", &[(i + 1).to_string(), format!("{}()", function), nice_el(v)])
}
fn correct_count(parameters: &[V], n: usize, function: &str) -> R<()> {
    if parameters.len() != n {
        return Err(err(
            "error_wrong_number_args",
            &[format!("{}()", function), n.to_string(), nice_el(&V::Tuple(Rc::new(parameters.to_vec())))],
        ));
    }
    Ok(())
}
fn no_params(parameters: &[V], function: &str) -> R<()> {
    if !parameters.is_empty() {
        return Err(err("error_expected_no_args", &[format!("{}()", function)]));
    }
    Ok(())
}
fn arg_dir(parameters: &[V], i: usize, function: &str) -> R<u8> {
    match &parameters[i] {
        V::Dir(d) => Ok(*d),
        v => Err(wrong_args(i, function, v)),
    }
}
fn arg_num(parameters: &[V], i: usize, function: &str) -> R<f64> {
    parameters[i].num().ok_or_else(|| wrong_args(i, function, &parameters[i]))
}
fn arg_const(parameters: &[V], i: usize, ns: u8, function: &str) -> R<&'static str> {
    match &parameters[i] {
        V::Const(n, name) if *n == ns => Ok(name),
        v => Err(wrong_args(i, function, v)),
    }
}
/// the "optional direction" pattern of get_entity_type / get_ground_type / measure / get_pos_z
fn opt_dir(parameters: &[V], function: &str) -> R<Option<u8>> {
    if parameters.is_empty() || (parameters.len() == 1 && parameters[0].is_none()) {
        return Ok(None);
    }
    correct_count(parameters, 1, function)?;
    Ok(Some(arg_dir(parameters, 0, function)?))
}

fn call_builtin(name: &'static str, parameters: Vec<V>, st: &StRef) -> R<f64> {
    let p = &parameters;
    let side = |se: SE| -> R<f64> {
        st.borrow_mut().set_se(se);
        Ok(0.0)
    };
    let ret = |v: V, ops: f64| -> R<f64> {
        st.borrow_mut().module_state.return_value = v;
        Ok(ops)
    };
    match name {
        "do_a_flip" => {
            no_params(p, name)?;
            side(SE::DoAFlip)
        }
        "pet_the_piggy" => {
            no_params(p, name)?;
            side(SE::PetThePiggy)
        }
        "tap" => {
            no_params(p, name)?;
            let secs = dur_seconds(st.borrow().sh.op_duration_ns.get());
            Ok((0.1 / secs).floor())
        }
        "print" => {
            let s = p.iter().map(nice).collect::<Vec<_>>().join(" ");
            side(SE::Print(s))
        }
        "quick_print" => {
            let s = p.iter().map(nice).collect::<Vec<_>>().join(" ");
            st.borrow().sh.log(&s);
            ret(V::None, 0.0)
        }
        "change_hat" => {
            correct_count(p, 1, name)?;
            side(SE::ChangeHat(arg_const(p, 0, NS_HATS, name)?))
        }
        "min" | "max" => {
            let is_max = name == "max";
            let key = if is_max { "error_wrong_use_of_max" } else { "error_wrong_use_of_min" };
            if p.is_empty() {
                return Err(err(key, &["[]".to_string()]));
            }
            let items: Vec<V> = if p.len() == 1 {
                if !is_enumerable(&p[0]) {
                    return Err(wrong_args(0, name, &p[0]));
                }
                enumerate(&p[0])
            } else {
                p.clone()
            };
            if items.is_empty() {
                return Err(err(key, &[nice_el(&p[0])]));
            }
            let mut steps = 0;
            let mut best = items[0].clone();
            for item in items.iter() {
                if deep_compare(item, &best, name, &mut steps)? * (if is_max { 1 } else { -1 }) > 0 {
                    best = item.clone();
                }
            }
            ret(best, OPERATION_OPS * steps.max(1) as f64)
        }
        "abs" => {
            correct_count(p, 1, name)?;
            ret(V::Num(arg_num(p, 0, name)?.abs()), OPERATION_OPS)
        }
        "swap" => {
            correct_count(p, 1, name)?;
            side(SE::Swap(arg_dir(p, 0, name)?))
        }
        "harvest" => {
            no_params(p, name)?;
            side(SE::Harvest)
        }
        "can_harvest" => {
            no_params(p, name)?;
            side(SE::CanHarvest)
        }
        "plant" => {
            correct_count(p, 1, name)?;
            side(SE::Plant(arg_const(p, 0, NS_ENTITIES, name)?))
        }
        "till" => {
            no_params(p, name)?;
            side(SE::Till)
        }
        "use_item" => {
            let num;
            if p.len() == 1 {
                num = 1;
            } else {
                correct_count(p, 2, name)?;
                arg_const(p, 0, NS_ITEMS, name)?;
                num = arg_num(p, 1, name)? as i32;
            }
            let item = arg_const(p, 0, NS_ITEMS, name)?;
            if num < 1 {
                return Err(err("error_negative_use_item", &[num.to_string()]));
            }
            side(SE::UseItem(item, num))
        }
        "get_water" => {
            no_params(p, name)?;
            side(SE::GetWater)
        }
        "move" => {
            correct_count(p, 1, name)?;
            side(SE::Move(arg_dir(p, 0, name)?))
        }
        "can_move" => {
            correct_count(p, 1, name)?;
            side(SE::CanMove(arg_dir(p, 0, name)?))
        }
        "get_entity_type" => side(SE::GetEntityType(opt_dir(p, name)?)),
        "get_ground_type" => side(SE::GetGroundType(opt_dir(p, name)?)),
        "measure" => side(SE::Measure(opt_dir(p, name)?)),
        "get_pos_z" => {
            opt_dir(p, name)?;
            side(SE::GetPosZ)
        }
        "get_time" => {
            no_params(p, name)?;
            side(SE::GetTime)
        }
        "get_tick_count" => {
            no_params(p, name)?;
            let v = {
                let s = st.borrow();
                s.h().op_count - s.start_op_count
            };
            ret(V::Num(v), 0.0)
        }
        "random" => {
            no_params(p, name)?;
            let v = st.borrow_mut().random_random.next_double();
            ret(V::Num(v), OPERATION_OPS)
        }
        "get_pos_x" => {
            no_params(p, name)?;
            side(SE::GetPosX)
        }
        "get_pos_y" => {
            no_params(p, name)?;
            side(SE::GetPosY)
        }
        "get_world_size" => {
            no_params(p, name)?;
            side(SE::GetWorldSize)
        }
        "range" => {
            let (start, end, step);
            if p.len() >= 3 {
                correct_count(p, 3, name)?;
                start = arg_num(p, 0, name)?;
                end = arg_num(p, 1, name)?;
                step = arg_num(p, 2, name)?;
            } else if p.len() == 2 {
                start = arg_num(p, 0, name)?;
                end = arg_num(p, 1, name)?;
                step = 1.0;
            } else {
                correct_count(p, 1, name)?;
                start = 0.0;
                end = arg_num(p, 0, name)?;
                step = 1.0;
            }
            if step.abs() < 0.01 {
                return Err("error_zero_step_size".into());
            }
            ret(V::Range(start, end, step), OPERATION_OPS)
        }
        "len" => {
            correct_count(p, 1, name)?;
            let n = match &p[0] {
                V::Dict(d) | V::Set(d) => d.borrow().len(),
                v if v.is_seq() => seq_len(v),
                v => return Err(wrong_args(0, name, v)),
            };
            ret(V::Num(n as f64), OPERATION_OPS)
        }
        "num_items" => {
            correct_count(p, 1, name)?;
            side(SE::NumItems(arg_const(p, 0, NS_ITEMS, name)?))
        }
        "get_cost" => {
            if !p.is_empty() && matches!(p[0], V::Const(NS_UNLOCKS, _)) {
                if p.len() == 1 {
                    side(SE::GetCost(p[0].clone(), None))
                } else {
                    correct_count(p, 2, name)?;
                    arg_num(p, 1, name)?;
                    side(SE::GetCost(p[0].clone(), Some(p[1].clone())))
                }
            } else {
                correct_count(p, 1, name)?;
                arg_const(p, 0, NS_ENTITIES, name)?;
                side(SE::GetCost(p[0].clone(), None))
            }
        }
        "get_companion" => {
            no_params(p, name)?;
            side(SE::GetCompanion)
        }
        "clear" => {
            no_params(p, name)?;
            side(SE::Clear)
        }
        "unlock" => {
            correct_count(p, 1, name)?;
            side(SE::Unlock(arg_const(p, 0, NS_UNLOCKS, name)?))
        }
        "num_unlocked" => {
            correct_count(p, 1, name)?;
            match &p[0] {
                V::Const(ns, _) if *ns == NS_UNLOCKS || *ns == NS_ITEMS || *ns == NS_HATS || *ns == NS_ENTITIES => {
                    side(SE::NumUnlocked(p[0].clone()))
                }
                v => Err(wrong_args(0, name, v)),
            }
        }
        "str" => {
            if p.is_empty() {
                return ret(new_str(""), OPERATION_OPS);
            }
            correct_count(p, 1, name)?;
            ret(new_str(&nice(&p[0])), OPERATION_OPS)
        }
        "list" => {
            if p.is_empty() {
                return ret(new_list(Vec::new()), OPERATION_OPS);
            }
            correct_count(p, 1, name)?;
            if !is_enumerable(&p[0]) {
                return Err(wrong_args(0, name, &p[0]));
            }
            if p[0].is_seq() && seq_len(&p[0]) > 100000 {
                return Err("error_sequence_too_large".into());
            }
            let items = enumerate(&p[0]);
            let n = items.len();
            ret(new_list(items), OPERATION_OPS * (1 + n) as f64)
        }
        "set" => {
            if p.is_empty() {
                return ret(V::Set(Rc::new(RefCell::new(DMap::new(true)))), OPERATION_OPS);
            }
            correct_count(p, 1, name)?;
            if !is_enumerable(&p[0]) {
                return Err(wrong_args(0, name, &p[0]));
            }
            if p[0].is_seq() && seq_len(&p[0]) > 100000 {
                return Err("error_sequence_too_large".into());
            }
            let mut set = DMap::new(true);
            for item in enumerate(&p[0]).iter() {
                if item.is_unhashable() {
                    return Err(err("error_bad_key", &[nice_el(item)]));
                }
                let key = to_key(item)?;
                if !set.contains(&key) {
                    set.insert_new(key, item.clone(), V::None);
                }
            }
            let n = set.len();
            ret(V::Set(Rc::new(RefCell::new(set))), OPERATION_OPS * (1 + n) as f64)
        }
        "dict" => {
            if p.is_empty() {
                return ret(V::Dict(Rc::new(RefCell::new(DMap::new(false)))), OPERATION_OPS);
            }
            correct_count(p, 1, name)?;
            let src = match &p[0] {
                V::Dict(d) => d.clone(),
                v => return Err(wrong_args(0, name, v)),
            };
            let mut copy = DMap::new(false);
            for (k, v) in src.borrow().entries().iter() {
                copy.put(to_key(k)?, k.clone(), v.clone());
            }
            let n = copy.len();
            ret(V::Dict(Rc::new(RefCell::new(copy))), OPERATION_OPS * (1 + 2 * n) as f64)
        }
        "set_execution_speed" => {
            correct_count(p, 1, name)?;
            side(SE::SetExecutionSpeed(arg_num(p, 0, name)?))
        }
        "set_world_size" => {
            correct_count(p, 1, name)?;
            side(SE::SetWorldSize(arg_num(p, 0, name)?))
        }
        "spawn_drone" => {
            match p.first() {
                Some(V::Func(f)) => {
                    if f.syntax_tree.is_none() {
                        return Err("error_spawn_drone_builtin".into());
                    }
                }
                Some(v) => return Err(wrong_args(0, name, v)),
                None => return Err(err("error_wrong_number_args", &["spawn_drone()".into(), "1".into(), "()".into()])),
            }
            side(SE::SpawnDrone(parameters.clone()))
        }
        "wait_for" | "has_finished" => {
            correct_count(p, 1, name)?;
            let h = match &p[0] {
                V::Handle(h) => h.clone(),
                v => return Err(wrong_args(0, name, v)),
            };
            side(if name == "wait_for" { SE::Await(h) } else { SE::HasFinished(h) })
        }
        "num_drones" => {
            no_params(p, name)?;
            side(SE::NumDrones)
        }
        "max_drones" => {
            no_params(p, name)?;
            side(SE::MaxDrones)
        }
        "append" => {
            correct_count(p, 2, name)?;
            match &p[0] {
                V::List(l) => l.borrow_mut().push(p[1].clone()),
                v => return Err(wrong_args(0, name, v)),
            }
            ret(V::None, OPERATION_OPS)
        }
        "add" => {
            correct_count(p, 2, name)?;
            let set = match &p[0] {
                V::Set(s) => s.clone(),
                v => return Err(wrong_args(0, name, v)),
            };
            if p[1].is_unhashable() {
                return Err(err("error_bad_key", &[nice_el(&p[1])]));
            }
            let key = to_key(&p[1])?;
            if !set.borrow().contains(&key) {
                set.borrow_mut().insert_new(key, p[1].clone(), V::None);
            }
            ret(V::None, OPERATION_OPS * py_size(&p[1]) as f64)
        }
        "remove" => {
            if let Some(V::List(l)) = p.first() {
                correct_count(p, 2, name)?;
                let mut steps = 0;
                let mut flag = false;
                let count = l.borrow().len();
                for i in 0..count {
                    let item = l.borrow()[i].clone();
                    if py_equals(&item, &p[1], &mut steps)? {
                        l.borrow_mut().remove(i);
                        flag = true;
                        steps += (l.borrow().len() - i) as i32;
                        break;
                    }
                }
                if !flag {
                    return Err(err("error_list_element_not_found", &[nice_el(&p[1])]));
                }
                return ret(V::None, OPERATION_OPS * steps as f64);
            }
            if let Some(V::Set(s)) = p.first() {
                correct_count(p, 2, name)?;
                let key = to_key(&p[1])?;
                if !s.borrow().contains(&key) {
                    return Err(err("error_set_element_not_found", &[nice_el(&p[1])]));
                }
                s.borrow_mut().remove(&key);
                return ret(V::None, OPERATION_OPS * py_size(&p[1]) as f64);
            }
            Err(err("error_remove_on_non_list_or_set", &[nice_el(p.first().unwrap_or(&V::None))]))
        }
        "pop" => {
            if let Some(V::List(l)) = p.first() {
                let mut num: i64 = -1;
                if p.len() > 1 {
                    correct_count(p, 2, name)?;
                    num = arg_num(p, 1, name)?.floor() as i32 as i64;
                }
                let count = l.borrow().len() as i64;
                if num < 0 {
                    num += count;
                }
                if num < 0 || num >= count {
                    return Err(err("error_index_out_of_bounds", &[num.to_string(), nice_el(&p[0])]));
                }
                let value = l.borrow_mut().remove(num as usize);
                let ops = OPERATION_OPS * (l.borrow().len() as i64 - num + 1) as f64;
                return ret(value, ops);
            }
            if let Some(V::Dict(d)) = p.first() {
                correct_count(p, 2, name)?;
                let key = to_key(&p[1])?;
                if !d.borrow().contains(&key) {
                    return Err(err("error_set_element_not_found", &[nice_el(&p[1])]));
                }
                let value = d.borrow_mut().remove(&key).unwrap();
                return ret(value, OPERATION_OPS * py_size(&p[1]) as f64);
            }
            Err(err("error_pop_on_non_dict_or_list", &[nice_el(p.first().unwrap_or(&V::None))]))
        }
        "insert" => {
            correct_count(p, 3, name)?;
            let l = match &p[0] {
                V::List(l) => l.clone(),
                v => return Err(wrong_args(0, name, v)),
            };
            let mut num = arg_num(p, 1, name)?.floor() as i32 as i64;
            let count = l.borrow().len() as i64;
            if num < 0 {
                num += count;
            }
            if num < 0 || num > count {
                return Err(err("error_index_out_of_bounds", &[num.to_string(), nice_el(&p[0])]));
            }
            let result = OPERATION_OPS * (count - num + 1) as f64;
            l.borrow_mut().insert(num as usize, p[2].clone());
            ret(V::None, result)
        }
        "place" | "leaderboard_run" | "simulate" | "dig" | "get_hardness" | "get_stability" | "prospect_iron"
        | "prospect_quartz" | "push" | "can_push" | "jump" | "hover" | "get_hover" => side(SE::NotPorted(name)),
        _ => Err(err("error_name_not_defined", &[name.to_string()])),
    }
}

// ---------------------------------------------------------------------------------------------
// Entities
// ---------------------------------------------------------------------------------------------
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum EC {
    Growable,
    Bush,
    Tree,
    Cactus,
    Pumpkin,
    DeadPumpkin,
    Sunflower,
    Hedge,
    Treasure,
    Dinosaur,
    Apple,
}

fn entity_class(so: &EntSO) -> Option<EC> {
    Some(match so.class {
        "Growable" => EC::Growable,
        "BushPlant" => EC::Bush,
        "TreePlant" => EC::Tree,
        "Cactus" => EC::Cactus,
        "Pumpkin" => EC::Pumpkin,
        "DeadPumpkin" => EC::DeadPumpkin,
        "Sunflower" => EC::Sunflower,
        "HedgePlant" => EC::Hedge,
        "Treasure" => EC::Treasure,
        "Dinosaur" => EC::Dinosaur,
        "Apple" => EC::Apple,
        _ => return None,
    })
}

struct Ent {
    so: &'static EntSO,
    class: EC,
    x: i32,
    y: i32,
    orientation: u8,
    // Growable
    is_grown: bool,
    grow_time: i64,
    prev_grow_time_factor: f64,
    grow_start: i64,
    grown_percent: f64,
    random_factor: f32,
    companion_type: &'static str,
    companion_pos: (i32, i32),
    weird: bool,
    grow_timer: Option<Rc<Timer>>,
    // Cactus / Sunflower
    number: i32,
    is_popped: bool,
    plant_time: i64,
    get_boost: bool,
    // Pumpkin
    mysterious_number: f64,
    // HedgePlant / Treasure
    walls: Rc<RefCell<[bool; 4]>>,
    maze_size: i32,
    low_left_corner: (i32, i32),
    removed: bool,
    treasure_factor: i32,
    next_pos: (i32, i32),
    start_time: i64,
    repositioning: bool,
    // Dinosaur
    is_in_snake: bool,
    can_move_to: bool,
    drone_uid: u64,
    // Apple
    apple_next_pos: (i32, i32),
    has_next_pos: bool,
}
type E = Rc<RefCell<Ent>>;

fn same(a: &E, b: &E) -> bool {
    Rc::ptr_eq(a, b)
}
fn eptr(e: &E) -> usize {
    Rc::as_ptr(e) as *const u8 as usize
}
fn is_growable(c: EC) -> bool {
    matches!(c, EC::Growable | EC::Bush | EC::Tree | EC::Cactus | EC::Pumpkin | EC::Sunflower | EC::Apple)
}
fn is_hedge(c: EC) -> bool {
    matches!(c, EC::Hedge | EC::Treasure)
}

#[derive(Clone)]
struct GridCell {
    entity: Option<E>,
    water_volume: f64,
    cactus_number: i32,
    ground: &'static str,
}

enum TimerFn {
    Grow(E),
    WaterDecay,
    ReceiveWater,
    ReceiveFertilizer,
    UsePower,
    CompleteRepositioning(E),
}
struct Timer {
    func: TimerFn,
    stopped: Cell<bool>,
}

#[derive(Clone, Copy, PartialEq, Eq)]
struct RectInt {
    x: i32,
    y: i32,
    w: i32,
    h: i32,
}
impl RectInt {
    fn x_max(&self) -> i32 {
        self.x + self.w
    }
    fn y_max(&self) -> i32 {
        self.y + self.h
    }
    fn positions(&self) -> Vec<(i32, i32)> {
        let mut out = Vec::new();
        for i in self.x..=self.x_max() {
            for j in self.y..=self.y_max() {
                out.push((i, j));
            }
        }
        out
    }
}

struct DinosaurHat {
    tail: VecDeque<E>,
    target: Option<E>,
    free_cells: Vec<(i32, i32)>,
    snake_surface: HashSet<(i32, i32)>,
    ops: i32,
    equip_time: i64,
}

struct Hat {
    name: &'static str,
    default_hat: bool,
    dino: Option<Box<DinosaurHat>>,
}

fn create_hat(name: &'static str, is_default: bool) -> Hat {
    let dino = if name == "dinosaur_hat" {
        Some(Box::new(DinosaurHat {
            tail: VecDeque::new(),
            target: None,
            free_cells: Vec::new(),
            snake_surface: HashSet::new(),
            ops: 400,
            equip_time: 0,
        }))
    } else {
        None
    };
    Hat { name, default_hat: is_default, dino }
}
/// HatSO.preventWrapping / preventHover: only the dinosaur hat has them on the surface farm
fn hat_prevents_wrapping(name: &str) -> bool {
    name == "dinosaur_hat"
}

struct Drone {
    x: i32,
    y: i32,
    drone_id: i32,
    uid: u64,
    flight_height: i32,
    hat: Hat,
}

/// slots in Execution::hot: drone ids stay below this
const MAX_DRONE_SLOTS: usize = 1024;

struct Execution {
    states: Vec<Option<StRef>>,
    /// each drone's Hot record, by drone id; allocated once, so the drones' pointers into it hold
    hot: Vec<Hot>,
    main_state: Option<StRef>,
    global_op_count: f64,
    next_execution_time: i64,
    stopped: bool,
}

type Items = Vec<f64>;
fn empty_items() -> Items {
    vec![0.0; ITEM_NAMES.len()]
}
fn one_item(name: &str, n: f64) -> Items {
    let mut it = empty_items();
    it[item_id(name)] = n;
    it
}
fn cost_block(cost: &[(&str, f64)], factor: f64) -> Items {
    let mut it = empty_items();
    for (name, n) in cost {
        it[item_id(name)] = n * factor;
    }
    it
}

const DIRS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];
fn reverse_dir(d: u8) -> u8 {
    (d + 2) % 4
}

// ---------------------------------------------------------------------------------------------
// Simulation + Farm + GridManager + controllers + Execution, in one struct
// ---------------------------------------------------------------------------------------------
struct Sim {
    sh: Rc<Shared>,
    /// skip_busy_waits' list of drones it moves on (index, ops per pass), kept between calls
    waiting_scratch: Vec<(usize, f64)>,
    // Simulation
    timers: PriorityQueue<Rc<Timer>>,
    current_time: i64,
    op_duration: i64,
    speed_factor: f64,
    paused: bool,
    has_error: bool,
    random_various: SysRandom,
    random_maze: SysRandom,
    random_snake: SysRandom,
    random_cactus: SysRandom,
    random_sunflower: SysRandom,
    random_pumpkin: SysRandom,
    random_poly: SysRandom,
    random_random: SysRandom,
    execution: Option<Execution>,
    // Farm
    drones: Vec<Option<Drone>>,
    main_drone_id: usize,
    drone_generation: i32,
    items: Items,
    unlocks: FxMap<String, i32>,
    used_power: f64,
    num_speed_upgrades: i32,
    next_uid: u64,
    max_drones_override: Option<i32>,
    // GridManager
    cells: Vec<GridCell>,
    wx: i32,
    wy: i32,
    size_limit: i32,
    world_size_override: (i32, i32),
    had_incorrect_sunflower_harvest: bool,
    // PumpkinController
    pumpkins: HashMap<(i32, i32), E>,
    groups: HashMap<usize, RectInt>,
    // harness bookkeeping
    collected: Vec<(i64, Items)>,
    error: Option<String>,
    finished: bool,
    // Achievements: the "items/min (highest: ...)" numbers of the inventory tooltip
    stat_window: VecDeque<(usize, f64, i64)>,
    stat_sum: Items,
    stat_best: Items,
}

static START_UNLOCKS: &[&str] = &[
    "grass", "soil", "harvest", "pass", "do_a_flip", "pet_the_piggy", "grassland", "hay", "straw_hat", "tap", "stats",
    "comments",
];

impl Sim {
    /// new Simulation(...) followed by new Farm(...)
    fn new(sh: Rc<Shared>, unlocks: &[String], items: Items, seed: i32, world_size_override: (i32, i32), max_drones_override: Option<i32>) -> Sim {
        let mut random = SysRandom::new(seed);
        let mut new_crop_random = || SysRandom::new(just_sha256_it(&mut random));
        let random_various = new_crop_random();
        let random_maze = new_crop_random();
        let random_snake = new_crop_random();
        let random_cactus = new_crop_random();
        let random_sunflower = new_crop_random();
        let random_pumpkin = new_crop_random();
        let random_poly = new_crop_random();
        let random_random = new_crop_random();
        let mut sim = Sim {
            sh,
            timers: PriorityQueue::new(),
            current_time: 0,
            op_duration: 2500000,
            speed_factor: 1.0,
            paused: false,
            has_error: false,
            random_various,
            random_maze,
            random_snake,
            random_cactus,
            random_sunflower,
            random_pumpkin,
            random_poly,
            random_random,
            execution: None,
            drones: Vec::new(),
            main_drone_id: 0,
            drone_generation: 0,
            items,
            unlocks: FxMap::default(),
            used_power: 0.0,
            waiting_scratch: Vec::new(),
            num_speed_upgrades: 0,
            next_uid: 1,
            max_drones_override,
            cells: Vec::new(),
            wx: 0,
            wy: 0,
            size_limit: 0,
            world_size_override,
            had_incorrect_sunflower_harvest: false,
            pumpkins: HashMap::new(),
            groups: HashMap::new(),
            collected: Vec::new(),
            error: None,
            finished: false,
            stat_window: VecDeque::new(),
            stat_sum: empty_items(),
            stat_best: empty_items(),
        };
        // GridManager constructor
        sim.start_timer(TimerFn::WaterDecay, dur_from_seconds(0.1));
        // Farm constructor
        let d = sim.new_drone(0, 0, 0);
        sim.drones.push(Some(d));
        for s in START_UNLOCKS {
            sim.unlock(s, 1);
        }
        let mut expand: Option<&String> = None;
        for u in unlocks {
            if u.starts_with("expand") {
                expand = Some(u);
            } else {
                sim.apply_unlock(u);
            }
        }
        match expand {
            None => sim.generate_world(),
            Some(u) => sim.apply_unlock(u),
        }
        if sim.cells.is_empty() {
            sim.generate_world();
        }
        let w = sim.num_unlocked("watering");
        sim.start_timer(TimerFn::ReceiveWater, dur_from_seconds(20.0 / (1i64 << w) as f64));
        let f = sim.num_unlocked("fertilizer");
        sim.start_timer(TimerFn::ReceiveFertilizer, dur_from_seconds(20.0 / (1i64 << f) as f64));
        sim.start_timer(TimerFn::UsePower, dur_from_seconds(0.2));
        let m = sim.max_speed_factor();
        sim.change_execution_speed(m);
        sim
    }

    fn set_time(&mut self, t: i64) {
        self.current_time = t;
        self.sh.current_time.set(t);
    }

    // ---- Simulation -------------------------------------------------------------------------
    fn start_timer(&mut self, func: TimerFn, time: i64) -> Rc<Timer> {
        let timer = Rc::new(Timer { func, stopped: Cell::new(false) });
        self.timers.enqueue(timer.clone(), self.current_time + time);
        timer
    }

    fn change_execution_speed(&mut self, speed_factor: f64) {
        self.op_duration = (2500000.0 / speed_factor).ceil() as i64;
        self.sh.op_duration_ns.set(self.op_duration);
        self.speed_factor = speed_factor;
    }

    fn add_ops_to_current_time(&mut self, ops: f64) {
        let t = self.current_time + dur_mul(self.op_duration, ops);
        self.set_time(t);
    }

    fn is_executing(&self) -> bool {
        self.execution.is_some()
    }

    fn stop_program_execution(&mut self) {
        if self.execution.is_some() {
            self.execution = None;
            let m = self.max_speed_factor();
            self.change_execution_speed(m);
            self.has_error = false;
            if self.size_limit > 0 {
                self.set_size_limit(0);
            }
            self.remove_spawned_drones();
            self.paused = false;
            self.finished = true;
        }
    }

    fn run_timer(&mut self, timer: Rc<Timer>) {
        match &timer.func {
            TimerFn::Grow(e) => self.grow(&e.clone()),
            TimerFn::WaterDecay => self.water_decay(),
            TimerFn::ReceiveWater => {
                if self.num_unlocked("watering") > 0 {
                    self.items[item_id("water")] += 1.0;
                }
                let w = self.num_unlocked("watering");
                self.start_timer(TimerFn::ReceiveWater, dur_from_seconds(20.0 / (1i64 << w) as f64));
            }
            TimerFn::ReceiveFertilizer => {
                if self.num_unlocked("fertilizer") > 0 {
                    self.items[item_id("fertilizer")] += 1.0;
                }
                let f = self.num_unlocked("fertilizer");
                self.start_timer(TimerFn::ReceiveFertilizer, dur_from_seconds(20.0 / (1i64 << f) as f64));
            }
            TimerFn::UsePower => self.use_power(),
            TimerFn::CompleteRepositioning(e) => self.complete_repositioning(&e.clone()),
        }
    }

    /// Simulation.RunNextStep; returns true when the simulation thread would wait for the next frame
    fn run_next_step(&mut self, goal_time: i64) -> bool {
        if self.paused {
            return true;
        }
        if self.is_executing() && self.has_error {
            self.stop_program_execution();
        }
        loop {
            match self.timers.peek() {
                Some((element, _)) if self.current_time < goal_time && element.stopped.get() => {
                    self.timers.dequeue();
                }
                _ => break,
            }
        }
        let exec_due = match &self.execution {
            Some(ex) => ex.next_execution_time <= goal_time,
            None => false,
        };
        let timer_priority = self.timers.peek().map(|t| t.1);
        if !exec_due && !matches!(timer_priority, Some(p) if p <= goal_time) {
            self.set_time(goal_time);
            return true;
        }
        if let Some(priority2) = timer_priority {
            let timer_first = match &self.execution {
                Some(ex) => ex.next_execution_time >= priority2,
                None => true,
            };
            if timer_first {
                self.set_time(priority2);
                let (timer, _) = self.timers.dequeue().unwrap();
                self.run_timer(timer);
                return false;
            }
        }
        let next = self.execution.as_ref().unwrap().next_execution_time;
        self.set_time(next);
        self.paused = false;
        let mut priority2 = timer_priority.unwrap_or(0);
        priority2 -= 1;
        let target_run_time = priority2.min(goal_time) - self.current_time;
        self.execute(target_run_time);
        false
    }

    // ---- Farm -------------------------------------------------------------------------------
    fn num_unlocked(&self, unlock: &str) -> i32 {
        *self.unlocks.get(unlock).unwrap_or(&0)
    }
    fn is_unlocked(&self, s: &str) -> bool {
        self.num_unlocked(&s.to_lowercase()) > 0
    }

    /// the local function applyUnlock in the Farm constructor
    fn apply_unlock(&mut self, s: &str) {
        let (text2, result) = match s.rfind('_') {
            Some(num) if !s.starts_with("debug") && s[num + 1..].parse::<i32>().is_ok() => {
                let level = s[num + 1..].parse::<i32>().unwrap();
                let name = s[..num].to_string();
                self.unlock(&name, level);
                (name, level)
            }
            _ => (s.to_string(), 1),
        };
        if let Some(so) = unlock_so(&text2) {
            self.unlock(&text2, result);
            self.unlock_all_in(so);
        } else {
            self.unlock(&text2, result);
        }
    }

    fn unlock(&mut self, s: &str, level: i32) {
        let text = s.to_lowercase();
        if self.num_unlocked(&text) == level {
            return;
        }
        self.unlocks.insert(text.clone(), level);
        match text.as_str() {
            "expand" => {
                self.size_limit = 0;
                self.generate_world();
            }
            "speed" => {
                let num = self.max_speed_factor();
                self.num_speed_upgrades = level;
                if self.speed_factor == num {
                    let m = self.max_speed_factor();
                    self.change_execution_speed(m);
                }
            }
            _ => {}
        }
    }

    fn unlock_all_in(&mut self, so: &'static UnlockSO) {
        for unlock2 in so.unlocks {
            let first = unlock2.chars().next().unwrap();
            if *unlock2 == so.name || (first.is_ascii_digit() && first.to_digit(10).unwrap() as i32 > self.num_unlocked(so.name)) {
                continue;
            }
            let text: &str = if first.is_ascii_digit() { &unlock2[1..] } else { unlock2 };
            let was = self.is_unlocked(text);
            self.unlock(text, 1);
            if !was {
                if let Some(child) = unlock_so(text) {
                    self.unlock_all_in(child);
                }
            }
        }
    }

    fn get_unlock_cost(&self, so: &UnlockSO, num_unlocked: i32) -> Items {
        let num = if num_unlocked >= 0 { num_unlocked } else { self.num_unlocked(so.name) };
        if num >= so.max_level {
            return empty_items();
        }
        if so.max_level > 1 {
            let count = so.multi_cost.len() as i32;
            if num > 0 {
                if count < num {
                    let factor = so.multi_factor.powf((num - count) as f32) as f64;
                    let mut block = cost_block(so.multi_cost[(count - 1) as usize], factor);
                    for v in block.iter_mut() {
                        if *v > 0.0 {
                            // Helper.RoundToNDecimalDigits(v, 3), then TruncateNumbers
                            let digits = v.abs().log10().floor() as i32;
                            let unit = 10f64.powi(digits - 3 + 1);
                            *v = ((*v / unit).round_ties_even() * unit).trunc();
                        }
                    }
                    return block;
                }
                return cost_block(so.multi_cost[(num - 1) as usize], 1.0);
            }
        }
        cost_block(so.cost, 1.0)
    }

    fn unlock_or_upgrade(&mut self, so: &'static UnlockSO) -> bool {
        if self.num_unlocked(so.name) >= so.max_level
            || (!so.req.0.is_empty() && self.num_unlocked(so.req.0) < so.req.1)
        {
            return false;
        }
        let cost = self.get_unlock_cost(so, -1);
        if !self.items_remove(&cost) {
            return false;
        }
        let level = self.num_unlocked(so.name) + 1;
        self.unlock(so.name, level);
        self.unlock_all_in(so);
        true
    }

    fn items_contains(&self, other: &Items) -> bool {
        self.items.iter().zip(other.iter()).all(|(a, b)| a >= b)
    }
    fn items_remove(&mut self, other: &Items) -> bool {
        if !self.items_contains(other) {
            return false;
        }
        for (a, b) in self.items.iter_mut().zip(other.iter()) {
            *a = (*a - *b).max(0.0);
        }
        true
    }

    fn max_speed_factor(&self) -> f64 {
        let mut num = 1.5f64.powi(self.num_speed_upgrades);
        if self.items[item_id("power")] > 0.0 {
            num *= 2.0;
        }
        num
    }

    fn use_power(&mut self) {
        let p = item_id("power");
        if self.items[p] > 0.0 {
            if self.items[p] < self.used_power {
                self.items[p] = 0.0;
            } else {
                self.items[p] -= self.used_power;
            }
            if self.speed_factor > self.max_speed_factor() {
                let m = self.max_speed_factor();
                self.change_execution_speed(m);
            }
        }
        self.used_power = 0.0;
        self.start_timer(TimerFn::UsePower, dur_from_seconds(0.2));
    }

    /// Achievements.CollectItem with trackRate: a harvest that took `collection_duration` to grow is
    /// spread backwards over that time in one-second slices, and the tooltip shows the 60 s window sum.
    fn record_collected_item(&mut self, item: usize, mut number: f64, mut collection_duration: i64) {
        let threshold = dur_from_seconds(1.0);
        let interval = dur_from_seconds(60.0);
        if collection_duration > interval {
            number = (number * (interval as f64 / collection_duration as f64)).max(0.0);
            collection_duration = interval;
        }
        if collection_duration > threshold {
            let num = (collection_duration as f64 / threshold as f64) as i32;
            let number2 = number / num as f64;
            let mut duration = self.current_time;
            for _ in 0..num {
                let entry = (item, number2, duration);
                duration -= threshold;
                let mut j = 0;
                while j < self.stat_window.len() && self.stat_window[j].2 > duration {
                    j += 1;
                }
                self.stat_window.insert(j, entry);
            }
        } else {
            self.stat_window.push_front((item, number, self.current_time));
        }
        self.stat_sum[item] += number;
        self.update_stat_sum();
        if self.stat_sum[item] > self.stat_best[item] {
            self.stat_best[item] = self.stat_sum[item];
        }
    }

    /// Achievements.UpdateSum
    fn update_stat_sum(&mut self) {
        let interval = dur_from_seconds(60.0);
        while let Some(&(item, number, time)) = self.stat_window.back() {
            if !(self.current_time - time > interval) {
                break;
            }
            self.stat_window.pop_back();
            if self.stat_sum[item] < number {
                self.stat_sum[item] = 0.0;
            } else {
                self.stat_sum[item] -= number;
            }
        }
    }

    fn collect_items(&mut self, items: Option<Items>, collection_duration: i64) {
        let items = match items {
            Some(i) if i.iter().any(|v| *v != 0.0) => i,
            _ => return,
        };
        for i in 0..items.len() {
            if items[i] > 0.0 {
                self.record_collected_item(i, items[i], collection_duration);
            }
        }
        let p = item_id("power");
        let boost = self.items[p] == 0.0 && items[p] > 0.0 && self.speed_factor == self.max_speed_factor();
        for (a, b) in self.items.iter_mut().zip(items.iter()) {
            *a += *b;
        }
        if boost {
            self.used_power = 0.0;
            let m = self.max_speed_factor();
            self.change_execution_speed(m);
        }
        self.collected.push((self.current_time, items));
    }

    fn max_drones(&self) -> i32 {
        match self.max_drones_override {
            Some(n) => n,
            None => 1 << self.num_unlocked("megafarm"),
        }
    }

    fn new_drone(&mut self, x: i32, y: i32, drone_id: i32) -> Drone {
        self.next_uid += 1;
        Drone { x, y, drone_id, uid: self.next_uid, flight_height: 1, hat: create_hat("straw_hat", true) }
    }

    fn add_drone(&mut self, drone_id: usize) -> R<usize> {
        self.drone_generation += 1;
        let (x, y) = {
            let d = self.drones[drone_id].as_ref().unwrap();
            (d.x, d.y)
        };
        for i in 0..self.drones.len() {
            if self.drones[i].is_none() {
                let d = self.new_drone(x, y, i as i32);
                self.drones[i] = Some(d);
                return Ok(i);
            }
        }
        if self.drones.len() as i32 >= self.max_drones() {
            return Err("error_max_drones_reached".into());
        }
        let d = self.new_drone(x, y, self.drones.len() as i32);
        self.drones.push(Some(d));
        Ok(self.drones.len() - 1)
    }

    fn remove_spawned_drones(&mut self) {
        let mut num = self.drones.len() as i64 - 1;
        while num >= 0 {
            if num as usize != self.main_drone_id {
                self.on_remove_drone(num as usize);
                self.drones.remove(num as usize);
                if (num as usize) < self.main_drone_id {
                    self.main_drone_id -= 1;
                }
            }
            num -= 1;
        }
        self.main_drone_id = 0;
        if let Some(Some(d)) = self.drones.get_mut(0) {
            d.drone_id = 0;
        }
    }

    fn remove_drone(&mut self, drone_id: usize) {
        if drone_id == self.main_drone_id {
            for i in 0..self.drones.len() {
                if self.drones[i].is_some() && i != self.main_drone_id {
                    self.main_drone_id = i;
                    break;
                }
            }
        }
        self.on_remove_drone(drone_id);
        self.drones[drone_id] = None;
    }

    fn on_remove_drone(&mut self, drone_id: usize) {
        let hat = match self.drones[drone_id].as_mut() {
            Some(d) => std::mem::replace(&mut d.hat, create_hat("straw_hat", true)),
            None => return,
        };
        self.hat_on_unequip(hat);
    }

    // ---- GridManager ------------------------------------------------------------------------
    fn in_bounds(&self, x: i32, y: i32) -> bool {
        x >= 0 && y >= 0 && x < self.wx && y < self.wy
    }
    fn idx(&self, x: i32, y: i32) -> usize {
        (y * self.wx + x) as usize
    }
    fn wrap(&self, x: i32, y: i32) -> (i32, i32) {
        ((x + self.wx) % self.wx, (y + self.wy) % self.wy)
    }
    fn entity_at(&self, x: i32, y: i32) -> Option<E> {
        self.cells[self.idx(x, y)].entity.clone()
    }
    /// GetEntityOrNull / GetEntity<T>
    fn entity_or_null(&self, x: i32, y: i32) -> Option<E> {
        if !self.in_bounds(x, y) {
            return None;
        }
        self.entity_at(x, y)
    }
    fn neighbors(&self, x: i32, y: i32) -> [Option<E>; 4] {
        [
            self.entity_or_null(x, y + 1),
            self.entity_or_null(x + 1, y),
            self.entity_or_null(x, y - 1),
            self.entity_or_null(x - 1, y),
        ]
    }

    fn update_world_size(&mut self) {
        if self.world_size_override.0 > 0 && self.world_size_override.1 > 0 {
            self.wx = self.world_size_override.0;
            self.wy = self.world_size_override.1;
            if self.size_limit > 0 && self.size_limit < self.wy {
                self.wx = self.size_limit;
                self.wy = self.size_limit;
            }
            return;
        }
        let num = match self.num_unlocked("expand") {
            0 => 1,
            1 => 2,
            2 => 3,
            3 => 4,
            4 => 6,
            5 => 8,
            6 => 12,
            7 => 16,
            8 => 22,
            _ => 32,
        };
        if self.size_limit > 0 && self.size_limit < num {
            self.wx = self.size_limit;
            self.wy = self.size_limit;
        } else if num == 2 {
            self.wx = 1;
            self.wy = 3;
        } else {
            self.wx = num;
            self.wy = num;
        }
    }

    fn set_size_limit(&mut self, value: i32) {
        if value > 2 {
            self.size_limit = value;
            self.generate_world();
        } else if self.size_limit > 0 {
            self.size_limit = 0;
            self.generate_world();
        }
    }

    fn generate_world(&mut self) {
        for i in 0..self.cells.len() {
            let e = self.cells[i].entity.clone();
            if let Some(e) = e {
                self.free(&e);
            }
        }
        let (owx, owy) = (self.wx, self.wy);
        self.update_world_size();
        let old = std::mem::take(&mut self.cells);
        self.cells = vec![GridCell { entity: None, water_volume: 0.0, cactus_number: -1, ground: "grassland" }; (self.wx * self.wy) as usize];
        for j in 0..self.wy {
            for k in 0..self.wx {
                if !old.is_empty() && k < owx && j < owy {
                    let i = self.idx(k, j);
                    self.cells[i].water_volume = old[(j * owx + k) as usize].water_volume;
                }
            }
        }
        self.clear_grid();
    }

    fn clear_grid(&mut self) {
        // groundData = new GroundData(WorldSize): the surface is grassland again
        for c in self.cells.iter_mut() {
            c.ground = "grassland";
        }
        for j in 0..self.wy {
            for k in 0..self.wx {
                self.set_entity(k, j, "grass");
            }
        }
    }

    fn set_water_volume(&mut self, x: i32, y: i32, volume: f64) {
        let i = self.idx(x, y);
        let before = self.cells[i].water_volume;
        self.cells[i].water_volume = volume.clamp(0.0, 1.0);
        if self.cells[i].water_volume != before {
            if let Some(e) = self.cells[i].entity.clone() {
                self.update_farm_object(&e);
            }
        }
    }

    fn water_decay(&mut self) {
        for j in 0..self.wy {
            for k in 0..self.wx {
                if self.random_various.next_double() < 0.1 {
                    let w = self.cells[self.idx(k, j)].water_volume;
                    self.set_water_volume(k, j, w * 0.99);
                }
            }
        }
        self.start_timer(TimerFn::WaterDecay, dur_from_seconds(0.1));
    }

    fn set_ground(&mut self, x: i32, y: i32, ground: &'static str) {
        let i = self.idx(x, y);
        self.cells[i].ground = ground;
    }

    fn set_entity(&mut self, x: i32, y: i32, name: &str) -> E {
        if let Some(old) = self.entity_at(x, y) {
            self.free(&old);
        }
        let so = entity_so(name);
        let class = entity_class(so).expect("entity class is not ported");
        let e = Rc::new(RefCell::new(Ent {
            so,
            class,
            x,
            y,
            orientation: 2,
            is_grown: false,
            grow_time: 0,
            prev_grow_time_factor: 1.0,
            grow_start: 0,
            grown_percent: 0.0,
            random_factor: 0.0,
            companion_type: "",
            companion_pos: (0, 0),
            weird: false,
            grow_timer: None,
            number: 0,
            is_popped: false,
            plant_time: 0,
            get_boost: false,
            mysterious_number: 0.0,
            walls: Rc::new(RefCell::new([false; 4])),
            maze_size: 0,
            low_left_corner: (0, 0),
            removed: false,
            treasure_factor: 1,
            next_pos: (0, 0),
            start_time: 0,
            repositioning: false,
            is_in_snake: true,
            can_move_to: false,
            drone_uid: 0,
            apple_next_pos: (0, 0),
            has_next_pos: false,
        }));
        let i = self.idx(x, y);
        self.cells[i].entity = Some(e.clone());
        self.on_restart(&e);
        e
    }

    fn remove_entity(&mut self, x: i32, y: i32, regrow_grass: bool) {
        if let Some(e) = self.entity_at(x, y) {
            self.free(&e);
            if regrow_grass && self.cells[self.idx(x, y)].ground == "grassland" {
                self.set_entity(x, y, "grass");
            }
        }
    }

    fn free(&mut self, e: &E) {
        let (x, y) = {
            let b = e.borrow();
            (b.x, b.y)
        };
        if self.in_bounds(x, y) {
            let i = self.idx(x, y);
            if matches!(&self.cells[i].entity, Some(c) if same(c, e)) {
                self.cells[i].entity = None;
            }
        }
        self.on_free(e);
    }

    fn swap(&mut self, x: i32, y: i32, dir: u8) -> bool {
        let (x2, y2) = (x + DIRS[dir as usize].0, y + DIRS[dir as usize].1);
        if !self.in_bounds(x2, y2) {
            return false;
        }
        let (i, i2) = (self.idx(x, y), self.idx(x2, y2));
        let entity = self.cells[i].entity.clone();
        let entity2 = self.cells[i2].entity.clone();
        if matches!(&entity, Some(e) if !e.borrow().so.swappable) || matches!(&entity2, Some(e) if !e.borrow().so.swappable) {
            return false;
        }
        let n = self.cells[i].cactus_number;
        self.cells[i].cactus_number = self.cells[i2].cactus_number;
        self.cells[i2].cactus_number = n;
        match &entity {
            Some(e) => {
                self.cells[i2].entity = Some(e.clone());
                {
                    let mut b = e.borrow_mut();
                    b.x = x2;
                    b.y = y2;
                }
                self.update_farm_object(e);
                self.update_neighbors(x2, y2);
            }
            None => self.cells[i2].entity = None,
        }
        match &entity2 {
            Some(e) => {
                self.cells[i].entity = Some(e.clone());
                {
                    let mut b = e.borrow_mut();
                    b.x = x;
                    b.y = y;
                }
                self.update_farm_object(e);
                self.update_neighbors(x, y);
            }
            None => self.cells[i].entity = None,
        }
        true
    }

    // ---- Entity / Growable ------------------------------------------------------------------
    fn update_neighbors(&mut self, x: i32, y: i32) {
        for n in self.neighbors(x, y).iter().flatten() {
            self.update_farm_object(n);
        }
    }

    fn harvestable(&self, e: &E) -> bool {
        let b = e.borrow();
        match b.class {
            EC::Apple | EC::DeadPumpkin => false,
            EC::Treasure => !b.repositioning,
            EC::Hedge | EC::Dinosaur => true,
            _ => b.is_grown,
        }
    }

    fn grow_time_factor(&self, e: &E) -> f64 {
        let (x, y, class) = {
            let b = e.borrow();
            (b.x, b.y, b.class)
        };
        let mut num = 1.0;
        num += self.cells[self.idx(x, y)].water_volume * 4.0;
        let base = 1.0 / num;
        if class == EC::Tree {
            let mut num2 = 1.0;
            for n in self.neighbors(x, y).iter().flatten() {
                if n.borrow().so.name == "tree" {
                    num2 *= 2.0;
                }
            }
            return base * num2;
        }
        base
    }

    fn get_grow_time(&mut self, e: &E) -> i64 {
        let f = self.grow_time_factor(e);
        let mut b = e.borrow_mut();
        b.prev_grow_time_factor = f;
        dur_from_seconds(f * b.so.mean_grow as f64 * b.random_factor as f64)
    }

    fn stop_growing(&mut self, e: &E) {
        let mut b = e.borrow_mut();
        if !b.is_grown {
            if let Some(t) = &b.grow_timer {
                t.stopped.set(true);
            }
            if b.grow_time > 0 {
                b.grown_percent += (self.current_time - b.grow_start) as f64 / b.grow_time as f64;
            }
        }
    }

    fn try_schedule_grow(&mut self, e: &E) {
        if e.borrow().is_grown {
            return;
        }
        self.stop_growing(e);
        let gt = self.get_grow_time(e);
        let duration = {
            let mut b = e.borrow_mut();
            b.grow_time = gt;
            b.grow_start = self.current_time;
            dur_mul(gt, 1.0 - b.grown_percent)
        };
        if duration == 0 {
            self.grow(e);
            return;
        }
        let timer = self.start_timer(TimerFn::Grow(e.clone()), duration);
        e.borrow_mut().grow_timer = Some(timer);
    }

    fn grow(&mut self, e: &E) {
        let (x, y, class) = {
            let mut b = e.borrow_mut();
            b.is_grown = true;
            (b.x, b.y, b.class)
        };
        // OnFullyGrown
        match class {
            EC::Cactus => {
                let i = self.idx(x, y);
                self.cells[i].cactus_number = -1;
            }
            EC::Pumpkin => {
                if self.random_pumpkin.next_double() <= 0.2 {
                    self.set_entity(x, y, "dead_pumpkin");
                } else {
                    self.add_pumpkin(e);
                }
            }
            _ => {}
        }
        self.update_neighbors(x, y);
    }

    fn update_farm_object(&mut self, e: &E) {
        if !is_growable(e.borrow().class) {
            return;
        }
        if e.borrow().prev_grow_time_factor != self.grow_time_factor(e) {
            self.try_schedule_grow(e);
        }
    }

    fn restart_growth(&mut self, e: &E) {
        let r = self.random_various.next_double() as f32;
        {
            let mut b = e.borrow_mut();
            b.is_grown = false;
            b.grow_start = self.current_time;
            b.grown_percent = 0.0;
            let dev = b.so.grow_dev;
            b.random_factor = r * dev * 2f32 + 1f32 - dev;
        }
        let gt = self.get_grow_time(e);
        e.borrow_mut().grow_time = gt;
        self.try_schedule_grow(e);
    }

    fn fertilize(&mut self, e: &E, number: i32) {
        e.borrow_mut().weird = true;
        if e.borrow().is_grown {
            return;
        }
        self.stop_growing(e);
        let gt = self.get_grow_time(e);
        {
            let mut b = e.borrow_mut();
            b.grown_percent = (b.grown_percent + dur_from_seconds(2.0 * number as f64) as f64 / gt as f64).min(1.0);
        }
        self.try_schedule_grow(e);
    }

    fn toggle_weird(&mut self, e: &E) {
        let (x, y) = {
            let mut b = e.borrow_mut();
            b.weird = !b.weird;
            (b.x, b.y)
        };
        self.random_various.next_max(1);
        for n in self.neighbors(x, y).iter().flatten() {
            let ok = {
                let b = n.borrow();
                is_growable(b.class) && b.so.can_be_weird
            };
            if ok {
                let mut b = n.borrow_mut();
                b.weird = !b.weird;
                drop(b);
                self.random_various.next_max(1);
            }
        }
    }

    fn choose_companion(&mut self, e: &E) {
        let (x, y, own) = {
            let b = e.borrow();
            (b.x, b.y, b.so.name)
        };
        let num = 3;
        let mut cp;
        loop {
            cp = (self.random_poly.next_range(-num, num + 1), self.random_poly.next_range(-num, num + 1));
            let w = self.wrap(x + cp.0, y + cp.1);
            if !((w == (x, y) || cp.0.abs() + cp.1.abs() > num) && self.wy != 1) {
                break;
            }
        }
        let pos = self.wrap(x + cp.0, y + cp.1);
        let mut ty;
        loop {
            ty = match self.random_poly.next_max(4) {
                2 => "carrot",
                1 => "bush",
                0 => "grass",
                _ => "tree",
            };
            if ty != own {
                break;
            }
        }
        let mut b = e.borrow_mut();
        b.companion_pos = pos;
        b.companion_type = ty;
    }

    fn has_companion(&self, e: &E) -> bool {
        let b = e.borrow();
        if !b.so.companion {
            return false;
        }
        match self.entity_or_null(b.companion_pos.0, b.companion_pos.1) {
            Some(o) => {
                if same(&o, e) {
                    b.so.name == b.companion_type
                } else {
                    o.borrow().so.name == b.companion_type
                }
            }
            None => false,
        }
    }

    /// Entity.YieldFactor with the Growable and Sunflower overrides
    fn yield_factor(&self, e: &E) -> f64 {
        let (class, upgrade, boost) = {
            let b = e.borrow();
            (b.class, b.so.yield_upgrade, b.get_boost)
        };
        let n = self.num_unlocked(upgrade);
        let mut f = (1i32.wrapping_shl((n - 1) as u32)).max(1) as f64;
        if is_growable(class) {
            if self.has_companion(e) {
                f *= (5i32 << self.num_unlocked("polyculture")) as f64;
            }
            if class == EC::Sunflower && boost {
                f *= 8.0;
            }
        }
        f
    }

    /// Growable.GetYield
    fn growable_get_yield(&self, e: &E) -> Items {
        let mut block = empty_items();
        let (drop_amount, drop_item, weird) = {
            let b = e.borrow();
            (b.so.drop_amount, b.so.drop_item, b.weird)
        };
        if drop_amount <= 0.0 {
            return block;
        }
        let mut num = drop_amount * self.yield_factor(e);
        if weird {
            num *= 0.5;
            block[item_id("weird_substance")] += num.trunc();
            num = num.ceil();
        }
        block[item_id(drop_item)] += num;
        block
    }

    /// Entity.Harvest and every override; None is the C# null (nothing collected, nothing removed)
    fn entity_harvest(&mut self, e: &E) -> Option<Items> {
        let (x, y, class) = {
            let b = e.borrow();
            (b.x, b.y, b.class)
        };
        match class {
            EC::Dinosaur => None,
            EC::DeadPumpkin => {
                self.remove_entity(x, y, true);
                None
            }
            EC::Apple => Some(empty_items()),
            EC::Hedge => {
                self.remove_maze(e);
                None
            }
            EC::Treasure => {
                if e.borrow().repositioning {
                    return Some(empty_items());
                }
                self.remove_maze(e);
                let size = e.borrow().maze_size as f64;
                let n = e.borrow().so.drop_amount * size * size * self.yield_factor(e);
                Some(one_item("gold", n))
            }
            EC::Cactus => Some(self.cactus_harvest(e)),
            EC::Pumpkin => {
                let (size, num_weird) = self.remove_pumpkin(e);
                Some(self.pumpkin_drops(e, size, num_weird))
            }
            EC::Sunflower => {
                let mut max = i32::MIN;
                let mut count = 0;
                for c in self.cells.iter() {
                    if let Some(s) = &c.entity {
                        let b = s.borrow();
                        if b.class == EC::Sunflower {
                            count += 1;
                            max = max.max(b.number);
                        }
                    }
                }
                let mut boost = e.borrow().number == max && count >= 10;
                let had = self.had_incorrect_sunflower_harvest;
                self.had_incorrect_sunflower_harvest = !boost;
                if had {
                    boost = false;
                }
                e.borrow_mut().get_boost = boost;
                self.growable_harvest(e)
            }
            _ => self.growable_harvest(e),
        }
    }

    fn growable_harvest(&mut self, e: &E) -> Option<Items> {
        let result = if self.harvestable(e) { self.growable_get_yield(e) } else { empty_items() };
        let (x, y) = {
            let b = e.borrow();
            (b.x, b.y)
        };
        self.remove_entity(x, y, true);
        Some(result)
    }

    fn on_restart(&mut self, e: &E) {
        let (so, class, x, y) = {
            let b = e.borrow();
            (b.so, b.class, b.x, b.y)
        };
        // Entity.OnRestart
        let orientation = if so.random_rotation { self.random_various.next_range(0, 4) as u8 } else { 2 };
        e.borrow_mut().orientation = orientation;
        if is_growable(class) {
            // gooIndex = randomVarious.Next(gooMeshes.Count - 1)
            self.random_various.next_max(1);
            if so.companion {
                self.choose_companion(e);
            }
            self.restart_growth(e);
        }
        match class {
            EC::Cactus => {
                let i = self.idx(x, y);
                if self.cells[i].cactus_number == -1 {
                    self.cells[i].cactus_number = self.random_cactus.next_max(10);
                }
                let mut b = e.borrow_mut();
                b.number = self.cells[i].cactus_number;
                b.is_popped = false;
                b.plant_time = self.current_time;
            }
            EC::Tree => self.update_neighbors(x, y),
            EC::Pumpkin => {
                let n = just_sha256_it(&mut self.random_pumpkin) as f64;
                e.borrow_mut().mysterious_number = n;
            }
            EC::Sunflower => {
                let n = self.random_sunflower.next_range(7, 16);
                e.borrow_mut().number = n;
            }
            EC::Treasure => {
                let mut b = e.borrow_mut();
                b.treasure_factor = 1;
                b.start_time = self.current_time;
                b.repositioning = false;
            }
            EC::Dinosaur => {
                let i = self.idx(x, y);
                if self.cells[i].ground == "grassland" {
                    self.cells[i].ground = "soil";
                }
            }
            _ => {}
        }
    }

    fn on_free(&mut self, e: &E) {
        let (class, x, y) = {
            let b = e.borrow();
            (b.class, b.x, b.y)
        };
        if is_growable(class) {
            self.stop_growing(e);
        }
        match class {
            EC::Tree => self.update_neighbors(x, y),
            EC::Pumpkin => {
                self.remove_pumpkin(e);
            }
            EC::Hedge | EC::Treasure => {
                self.remove_maze(e);
                e.borrow_mut().removed = true;
            }
            EC::Dinosaur => {
                let (in_snake, uid) = {
                    let b = e.borrow();
                    (b.is_in_snake, b.drone_uid)
                };
                if in_snake {
                    let di = self.drones.iter().position(|d| matches!(d, Some(d) if d.uid == uid));
                    if let Some(di) = di {
                        let wearing = {
                            let d = self.drones[di].as_ref().unwrap();
                            d.hat.name == "dinosaur_hat" && d.hat.dino.is_some()
                        };
                        if wearing {
                            let _ = self.drone_change_hat(di, create_hat("straw_hat", true));
                        }
                    }
                }
            }
            _ => {}
        }
    }

    fn entity_measure(&self, e: &E) -> Option<V> {
        let b = e.borrow();
        match b.class {
            EC::Cactus | EC::Sunflower => Some(V::Num(b.number as f64)),
            EC::Pumpkin => Some(V::Num(b.mysterious_number)),
            EC::Treasure => Some(tuple2(b.x as f64, b.y as f64)),
            EC::Hedge => {
                for i in b.low_left_corner.0..b.low_left_corner.0 + b.maze_size {
                    for j in b.low_left_corner.1..b.low_left_corner.1 + b.maze_size {
                        if let Some(t) = self.entity_or_null(i, j) {
                            if !same(&t, e) && t.borrow().class == EC::Treasure {
                                return Some(tuple2(i as f64, j as f64));
                            }
                        }
                    }
                }
                Some(V::None)
            }
            EC::Apple => {
                if !b.has_next_pos {
                    return Some(V::None);
                }
                let np = b.apple_next_pos;
                let next_is_dino = matches!(self.entity_or_null(np.0, np.1), Some(o) if !same(&o, e) && o.borrow().class == EC::Dinosaur);
                if next_is_dino {
                    let mut num = 0;
                    let mut empty: Option<(i32, i32)> = None;
                    for (i, c) in self.cells.iter().enumerate() {
                        match &c.entity {
                            Some(o) => {
                                if !same(o, e) && o.borrow().class == EC::Dinosaur {
                                    num += 1;
                                }
                            }
                            None => {
                                if empty.is_some() {
                                    return Some(tuple2(np.0 as f64, np.1 as f64));
                                }
                                empty = Some((i as i32 % self.wx, i as i32 / self.wx));
                            }
                        }
                    }
                    let num2 = self.wx * self.wy - 2;
                    if let (true, Some(p)) = (num == num2, empty) {
                        return Some(tuple2(p.0 as f64, p.1 as f64));
                    }
                }
                Some(tuple2(np.0 as f64, np.1 as f64))
            }
            _ => None,
        }
    }

    // ---- Cactus -----------------------------------------------------------------------------
    fn cactus_at(&self, x: i32, y: i32) -> Option<E> {
        match self.entity_or_null(x, y) {
            Some(e) if e.borrow().class == EC::Cactus => Some(e),
            _ => None,
        }
    }

    fn cactus_are_sorted(one: &Option<E>, two: &Option<E>) -> bool {
        let (a, b) = match (one, two) {
            (Some(a), Some(b)) => (a.borrow(), b.borrow()),
            _ => return true,
        };
        if !a.is_grown || !b.is_grown {
            return false;
        }
        let num = a.number - b.number;
        !(num != 0 && num > 0)
    }

    fn cactus_is_sorted(&self, c: &E) -> bool {
        let (x, y, grown) = {
            let b = c.borrow();
            (b.x, b.y, b.is_grown)
        };
        if !grown {
            return false;
        }
        let me = Some(c.clone());
        Sim::cactus_are_sorted(&me, &self.cactus_at(x, y + 1))
            && Sim::cactus_are_sorted(&me, &self.cactus_at(x + 1, y))
            && Sim::cactus_are_sorted(&self.cactus_at(x, y - 1), &me)
            && Sim::cactus_are_sorted(&self.cactus_at(x - 1, y), &me)
    }

    fn cactus_pop(&mut self, c: &E, popped: &mut Vec<E>, num_weird: &mut i32) {
        // The recursion of Cactus.Pop, with an explicit stack so a 32x32 field cannot overflow.
        let mut stack = vec![c.clone()];
        while let Some(cur) = stack.pop() {
            let (x, y) = {
                let mut b = cur.borrow_mut();
                if b.is_popped || !b.is_grown {
                    continue;
                }
                b.is_popped = true;
                if b.weird {
                    *num_weird += 1;
                }
                (b.x, b.y)
            };
            popped.push(cur.clone());
            let neighbors = [self.cactus_at(x, y + 1), self.cactus_at(x + 1, y), self.cactus_at(x, y - 1), self.cactus_at(x - 1, y)];
            if !neighbors.iter().all(|n| match n {
                None => true,
                Some(n) => self.cactus_is_sorted(n),
            }) {
                continue;
            }
            for n in neighbors.iter().rev().flatten() {
                stack.push(n.clone());
            }
        }
    }

    fn cactus_harvest(&mut self, c: &E) -> Items {
        let (x, y, grown) = {
            let b = c.borrow();
            (b.x, b.y, b.is_grown)
        };
        if !grown {
            self.remove_entity(x, y, true);
            return empty_items();
        }
        let mut list = Vec::new();
        let mut num_weird = 0;
        self.cactus_pop(c, &mut list, &mut num_weird);
        let count = list.len() as f64;
        for item in list.iter() {
            let (ix, iy) = {
                let b = item.borrow();
                (b.x, b.y)
            };
            self.remove_entity(ix, iy, true);
        }
        // GetDrops
        let num = self.yield_factor(c) * count;
        let num2 = (0.5 * num_weird as f64 * num).floor();
        let mut block = one_item("cactus", count * num - num2);
        if num2 > 0.0 {
            block[item_id("weird_substance")] += num2;
        }
        block
    }

    // ---- PumpkinController ------------------------------------------------------------------
    fn add_pumpkin(&mut self, p: &E) {
        let pos = {
            let b = p.borrow();
            (b.x, b.y)
        };
        self.pumpkins.insert(pos, p.clone());
        self.merge_with_others(pos);
    }

    /// returns (size.x, numWeird); size 0 means the pumpkin was not part of a group
    fn remove_pumpkin(&mut self, p: &E) -> (i32, i32) {
        let mut num_weird = 0;
        let rect = match self.groups.get(&eptr(p)) {
            Some(r) => *r,
            None => {
                let (x, y) = {
                    let b = p.borrow();
                    (b.x, b.y)
                };
                self.remove_entity(x, y, true);
                return (0, 0);
            }
        };
        for item in rect.positions() {
            if let Some(q) = self.pumpkins.get(&item).cloned() {
                self.groups.remove(&eptr(&q));
            }
            if let Some(e) = self.entity_at(item.0, item.1) {
                let b = e.borrow();
                if b.class == EC::Pumpkin && b.weird {
                    num_weird += 1;
                }
            }
            self.remove_entity(item.0, item.1, true);
            self.pumpkins.remove(&item);
        }
        (rect.w + 1, num_weird)
    }

    fn pumpkin_drops(&self, p: &E, size: i32, num_weird: i32) -> Items {
        let num = size.min(6) as f64 * self.yield_factor(p);
        let num2 = (num_weird as f64 * 0.5 * num).floor();
        let n = (size * size) as f64 * num - num2;
        let mut block = one_item("pumpkin", n);
        if num2 > 0.0 {
            block[item_id("weird_substance")] += num2;
        }
        block
    }

    fn merge_with_others(&mut self, pos: (i32, i32)) {
        let y = self.wy;
        let n = (y * y) as usize;
        // array[i].x is the size of the largest full square whose low-left corner is cell i
        let mut array = vec![0i32; n];
        for i in 0..n {
            if self.pumpkins.contains_key(&((i as i32) % y, (i as i32) / y)) {
                array[i] = 1;
            }
        }
        let mut flag = true;
        let mut num = 1;
        while flag {
            num += 1;
            flag = false;
            for j in 0..n {
                let num2 = j as i32 % y;
                let num3 = j as i32 / y;
                if num2 + 1 < y && num3 + 1 < y {
                    let a = array[j];
                    let b = array[(num2 + 1 + y * num3) as usize];
                    let c = array[(num2 + y * (num3 + 1)) as usize];
                    let d = array[(num2 + 1 + y * (num3 + 1)) as usize];
                    if a == num - 1 && b == num - 1 && c == num - 1 && d == num - 1 {
                        array[j] = num;
                        flag = true;
                    }
                }
            }
        }
        num -= 1;
        let rect = self.largest_square(&array, y, num, pos);
        let positions = rect.positions();
        let first = self.pumpkins[&positions[0]].clone();
        let mysterious = first.borrow().mysterious_number;
        for item in positions {
            let q = self.pumpkins[&item].clone();
            self.groups.insert(eptr(&q), rect);
            q.borrow_mut().mysterious_number = mysterious;
        }
    }

    fn largest_square(&self, dp: &[i32], n: i32, mut square_size: i32, pos: (i32, i32)) -> RectInt {
        while square_size > 1 {
            for i in 0..dp.len() {
                let r = RectInt { x: i as i32 % n, y: i as i32 / n, w: square_size - 1, h: square_size - 1 };
                let in_rect = pos.0 >= r.x && pos.1 >= r.y && pos.0 <= r.x_max() && pos.1 <= r.y_max();
                if dp[i] >= square_size && in_rect && !self.has_overlaps(&r) {
                    return r;
                }
            }
            square_size -= 1;
        }
        RectInt { x: pos.0, y: pos.1, w: 0, h: 0 }
    }

    fn has_overlaps(&self, r: &RectInt) -> bool {
        for item in r.positions() {
            if let Some(q) = self.pumpkins.get(&item) {
                if let Some(g) = self.groups.get(&eptr(q)) {
                    if g.x_max() > r.x_max() || g.y_max() > r.y_max() || g.x < r.x || g.y < r.y {
                        return true;
                    }
                }
            }
        }
        false
    }

    // ---- Mazes ------------------------------------------------------------------------------
    fn remove_maze(&mut self, e: &E) {
        let (removed, size, corner) = {
            let b = e.borrow();
            (b.removed, b.maze_size, b.low_left_corner)
        };
        if removed {
            return;
        }
        for i in 0..size {
            for j in 0..size {
                let (x, y) = (i + corner.0, j + corner.1);
                if !self.in_bounds(x, y) {
                    continue;
                }
                if let Some(h) = self.entity_at(x, y) {
                    let hit = {
                        let b = h.borrow();
                        is_hedge(b.class) && !b.removed
                    };
                    if hit {
                        h.borrow_mut().removed = true;
                        self.remove_entity(x, y, true);
                    }
                }
            }
        }
    }

    /// BushPlant.GenerateHedgeMaze
    fn generate_hedge_maze(&mut self, bush: &E, desired_size: i32) {
        let pos = {
            let b = bush.borrow();
            (b.x, b.y)
        };
        let mut num = 1;
        let mut v = pos;
        let mut v2 = (-1, -1);
        let mut array = [false; 4];
        let idx = |d: (i32, i32)| -> usize { (if d.0 > 0 { 1 } else { 0 }) + (if d.1 > 0 { 2 } else { 0 }) };
        while num < desired_size {
            let mut v3 = v;
            let mut v4 = v;
            if v2.0 > 0 {
                v3.1 += if v2.1 > 0 { num } else { -1 };
                v4.0 += num;
                if v2.1 < 0 {
                    v4.1 += num - 1;
                }
            } else {
                v3.0 += num - 1;
                v3.1 += if v2.1 > 0 { num } else { -1 };
                v4.0 -= 1;
                if v2.1 < 0 {
                    v4.1 += num - 1;
                }
            }
            // every surface cell is at the same depth, so the strip is free if it is inside the farm
            if self.in_bounds(v3.0, v3.1) && self.in_bounds(v4.0, v4.1) {
                num += 1;
                if v2.0 < 0 {
                    v.0 -= 1;
                }
                if v2.1 < 0 {
                    v.1 -= 1;
                }
                v2 = (-v2.0, -v2.1);
                continue;
            }
            array[idx(v2)] = true;
            let mut num5 = 0;
            let mut found = false;
            while num5 < 3 {
                v2 = (-v2.1, v2.0);
                if array[idx(v2)] {
                    num5 += 1;
                    continue;
                }
                found = true;
                break;
            }
            if !found {
                break;
            }
        }
        let cells = (num * num) as usize;
        let mut array2: Vec<Option<[bool; 4]>> = vec![None; cells];
        let num6 = self.random_maze.next_max(num * num) as usize;
        array2[num6] = Some([true; 4]);
        let mut list = vec![num6];
        let mut flag = false;
        let mut list2: Vec<usize> = Vec::new();
        while let Some(&num7) = list.last() {
            let num8 = (num7 as i32) % num;
            let num9 = (num7 as i32) / num;
            // OrderBy(k => randomMaze.Next()): one key per direction, stable sort
            let mut order: Vec<(i32, u8)> = (0u8..4).map(|d| (self.random_maze.next(), d)).collect();
            order.sort_by_key(|k| k.0);
            for (_, item) in order.iter() {
                let dv = DIRS[*item as usize];
                let num10 = num8 + dv.0;
                let num11 = num9 + dv.1;
                if num10 >= 0 && num11 >= 0 && num10 < num && num11 < num && array2[(num10 + num * num11) as usize].is_none() {
                    let ni = (num10 + num * num11) as usize;
                    list.push(ni);
                    let mut w = [true; 4];
                    w[reverse_dir(*item) as usize] = false;
                    array2[ni] = Some(w);
                    array2[num7].as_mut().unwrap()[*item as usize] = false;
                    flag = false;
                    break;
                }
            }
            if *list.last().unwrap() == num7 {
                list.pop();
                if !flag {
                    list2.push(num7);
                    flag = true;
                }
            }
        }
        let num12 = list2[self.random_maze.next_max(list2.len() as i32 - 1) as usize];
        for num13 in 0..num {
            for num14 in 0..num {
                let flag2 = num12 == (num13 + num * num14) as usize;
                let (x, y) = (num13 + v.0, num14 + v.1);
                self.set_ground(x, y, "grassland");
                let hedge = self.set_entity(x, y, if flag2 { "treasure" } else { "hedge" });
                {
                    let mut b = hedge.borrow_mut();
                    b.walls = Rc::new(RefCell::new(array2[(num13 + num * num14) as usize].unwrap()));
                    b.low_left_corner = v;
                    b.maze_size = num;
                }
                if flag2 {
                    self.choose_next_position(&hedge);
                }
            }
        }
    }

    fn choose_next_position(&mut self, t: &E) {
        let (size, corner, pos) = {
            let b = t.borrow();
            (b.maze_size, b.low_left_corner, (b.x, b.y))
        };
        if size > 1 {
            loop {
                let np = (self.random_maze.next_max(size) + corner.0, self.random_maze.next_max(size) + corner.1);
                t.borrow_mut().next_pos = np;
                if np != pos {
                    break;
                }
            }
        }
    }

    fn is_in_same_maze(t: &E, hedge: &Option<E>) -> bool {
        match hedge {
            Some(h) => {
                if same(h, t) {
                    return !t.borrow().removed;
                }
                let (a, b) = (t.borrow(), h.borrow());
                is_hedge(b.class) && !b.removed && b.maze_size == a.maze_size && b.low_left_corner == a.low_left_corner
            }
            None => false,
        }
    }

    /// returns (result, useActionTicks)
    fn reposition_treasure(&mut self, t: &E, desired_size: i32) -> (bool, bool) {
        {
            let b = t.borrow();
            if b.maze_size <= 1 || desired_size < b.maze_size || b.treasure_factor >= 301 {
                return (false, false);
            }
            if b.repositioning {
                return (false, true);
            }
        }
        t.borrow_mut().repositioning = true;
        let size = t.borrow().maze_size as f64;
        let n = t.borrow().so.drop_amount * size * size * self.yield_factor(t);
        self.collect_items(Some(one_item("gold", n)), 0);
        let d = dur_mul(self.op_duration, 200.0);
        self.start_timer(TimerFn::CompleteRepositioning(t.clone()), d);
        (true, true)
    }

    fn complete_repositioning(&mut self, t: &E) {
        let (x, y, next, size, corner, factor, start_time, walls) = {
            let mut b = t.borrow_mut();
            if !b.repositioning || b.removed {
                return;
            }
            b.repositioning = false;
            (b.x, b.y, b.next_pos, b.maze_size, b.low_left_corner, b.treasure_factor, b.start_time, b.walls.clone())
        };
        if !self.in_bounds(x, y) || !matches!(self.entity_at(x, y), Some(c) if same(&c, t)) || !self.in_bounds(next.0, next.1) {
            return;
        }
        let hedge = self.entity_at(next.0, next.1);
        if !Sim::is_in_same_maze(t, &hedge) {
            return;
        }
        let hedge = hedge.unwrap();
        hedge.borrow_mut().removed = true;
        let hedge_walls = hedge.borrow().walls.clone();
        let obj = self.set_entity(next.0, next.1, "treasure");
        {
            let mut b = obj.borrow_mut();
            b.walls = hedge_walls;
            b.treasure_factor = factor + 1;
            b.start_time = start_time;
            b.maze_size = size;
            b.low_left_corner = corner;
        }
        self.choose_next_position(&obj);
        t.borrow_mut().removed = true;
        let obj2 = self.set_entity(x, y, "hedge");
        {
            let mut b = obj2.borrow_mut();
            b.walls = walls;
            b.maze_size = size;
            b.low_left_corner = corner;
        }
        // `this` is the old treasure: removed, but its size and corner still identify the maze
        let same_maze = |sim: &Sim, px: i32, py: i32| -> Option<E> {
            let h = sim.entity_or_null(px, py)?;
            let ok = {
                let b = h.borrow();
                is_hedge(b.class) && !b.removed && b.maze_size == size && b.low_left_corner == corner
            };
            if ok { Some(h) } else { None }
        };
        for i in corner.0..corner.0 + size {
            for j in corner.1..corner.1 + size {
                if (i + j) % 2 == 1 {
                    continue;
                }
                for item in 0u8..4 {
                    let (vx, vy) = (i + DIRS[item as usize].0, j + DIRS[item as usize].1);
                    if !(self.random_maze.next_double() > 0.002)
                        && vx >= corner.0
                        && vy >= corner.1
                        && vx < corner.0 + size
                        && vy < corner.1 + size
                    {
                        if let (Some(h2), Some(h3)) = (same_maze(self, i, j), same_maze(self, vx, vy)) {
                            h2.borrow().walls.borrow_mut()[item as usize] = false;
                            h3.borrow().walls.borrow_mut()[reverse_dir(item) as usize] = false;
                        }
                    }
                }
            }
        }
    }

    // ---- Hats -------------------------------------------------------------------------------
    fn apple_cost(&self) -> Items {
        let num = (self.num_unlocked("dinosaurs") - 1).max(0);
        cost_block(entity_so("apple").cost, (1i32 << num).max(1) as f64)
    }

    fn bone_count(&self) -> f64 {
        let num = self.cells.iter().filter(|c| matches!(&c.entity, Some(e) if e.borrow().class == EC::Dinosaur)).count();
        let num2 = (self.num_unlocked("dinosaurs") - 1).max(0);
        (num as f64).powf(2.0).floor() * (1i32 << num2) as f64
    }

    /// Drone.ChangeHat(Hat newHat, ...)
    fn drone_change_hat(&mut self, di: usize, new_hat: Hat) -> R<()> {
        let old = std::mem::replace(&mut self.drones[di].as_mut().unwrap().hat, new_hat);
        self.hat_on_unequip(old);
        self.hat_on_equip(di)
    }

    fn hat_on_unequip(&mut self, hat: Hat) {
        let mut dino = match hat.dino {
            Some(d) => d,
            None => return,
        };
        if !dino.tail.is_empty() {
            let n = self.bone_count();
            let since_equip = self.current_time - dino.equip_time;
            self.collect_items(Some(one_item("bone", n)), since_equip);
        }
        let tail: Vec<E> = dino.tail.iter().cloned().collect();
        for item in tail.iter() {
            let (x, y) = {
                let mut b = item.borrow_mut();
                b.is_in_snake = false;
                (b.x, b.y)
            };
            self.remove_entity(x, y, true);
        }
        self.dino_remove_apple(&mut dino);
        dino.tail.clear();
    }

    fn dino_remove_apple(&mut self, dino: &mut DinosaurHat) {
        if let Some(t) = dino.target.take() {
            let (x, y) = {
                let b = t.borrow();
                (b.x, b.y)
            };
            if matches!(self.entity_or_null(x, y), Some(c) if same(&c, &t)) {
                self.remove_entity(x, y, true);
            }
        }
    }

    fn hat_on_equip(&mut self, di: usize) -> R<()> {
        if self.drones[di].as_ref().unwrap().hat.name != "dinosaur_hat" {
            return Ok(());
        }
        let wearing = self.drones.iter().filter(|d| matches!(d, Some(d) if d.hat.name == "dinosaur_hat")).count();
        if wearing > 1 {
            self.drones[di].as_mut().unwrap().hat = create_hat("straw_hat", true);
            return Err("error_dino_hat_already_used".into());
        }
        let mut dino = self.drones[di].as_mut().unwrap().hat.dino.take().unwrap();
        dino.equip_time = self.current_time;
        let (x, y) = {
            let d = self.drones[di].as_ref().unwrap();
            (d.x, d.y)
        };
        let free_here = match self.entity_at(x, y) {
            None => true,
            Some(e) => e.borrow().so.overplant,
        };
        if free_here {
            let cost = self.apple_cost();
            dino.snake_surface = self.find_free_cells((x, y), &mut dino.free_cells);
            let mut target_pos = (0, 0);
            if self.items_contains(&cost) && self.try_choose_target(&dino.free_cells, &mut target_pos, Some((x, y))) {
                self.items_remove(&cost);
                let apple = self.set_entity(x, y, "apple");
                {
                    let mut b = apple.borrow_mut();
                    b.apple_next_pos = target_pos;
                    b.has_next_pos = true;
                }
                dino.target = Some(apple);
            } else {
                self.sh.warn("warning_missing_seed [Entities.Apple]".into());
            }
        }
        if let Some(d) = self.drones[di].as_mut() {
            if d.hat.name == "dinosaur_hat" {
                d.hat.dino = Some(dino);
            }
        }
        Ok(())
    }

    fn find_free_cells(&self, drone_pos: (i32, i32), free_cells: &mut Vec<(i32, i32)>) -> HashSet<(i32, i32)> {
        free_cells.clear();
        let mut hash_set = HashSet::new();
        hash_set.insert(drone_pos);
        let mut list: Vec<(i32, i32)> = DIRS.iter().map(|d| (drone_pos.0 + d.0, drone_pos.1 + d.1)).collect();
        while let Some(v) = list.pop() {
            if !self.in_bounds(v.0, v.1) {
                continue;
            }
            if hash_set.insert(v) {
                list.extend(DIRS.iter().map(|d| (v.0 + d.0, v.1 + d.1)));
                let occupied =
                    matches!(self.entity_at(v.0, v.1), Some(e) if matches!(e.borrow().class, EC::Dinosaur | EC::Apple));
                if !occupied {
                    free_cells.push(v);
                }
            }
        }
        hash_set
    }

    fn try_choose_target(&mut self, free_cells: &[(i32, i32)], target_pos: &mut (i32, i32), current: Option<(i32, i32)>) -> bool {
        if self.wy <= 1 {
            return false;
        }
        if free_cells.is_empty() || (free_cells.len() == 1 && Some(free_cells[0]) == current) {
            return false;
        }
        loop {
            *target_pos = free_cells[self.random_snake.next_max(free_cells.len() as i32) as usize];
            if Some(*target_pos) != current {
                break;
            }
        }
        true
    }

    /// DinosaurHat.OnMove
    fn dino_on_move(&mut self, di: usize, old_pos: (i32, i32), new_pos: (i32, i32)) -> i32 {
        let mut dino = self.drones[di].as_mut().unwrap().hat.dino.take().unwrap();
        let uid = self.drones[di].as_ref().unwrap().uid;
        let mut flag = false;
        let hash_set = self.find_free_cells(old_pos, &mut dino.free_cells);
        if dino.target.is_some() && dino.snake_surface != hash_set {
            self.dino_remove_apple(&mut dino);
        }
        let num = self.wx * self.wy - 2;
        let on_apple = match &dino.target {
            Some(t) => {
                let b = t.borrow();
                (b.x, b.y) == old_pos && matches!(self.entity_at(old_pos.0, old_pos.1), Some(c) if same(&c, t))
            }
            None => false,
        };
        if on_apple {
            let cost = self.apple_cost();
            let flag2 = self.items_contains(&cost);
            flag = true;
            let next = dino.target.as_ref().unwrap().borrow().apple_next_pos;
            let next_free = match self.entity_at(next.0, next.1) {
                None => true,
                Some(e) => e.borrow().so.overplant,
            };
            let mut target_pos = (0, 0);
            if next_free && flag2 && self.try_choose_target(&dino.free_cells, &mut target_pos, Some(next)) {
                self.items_remove(&cost);
                let apple = self.set_entity(next.0, next.1, "apple");
                {
                    let mut b = apple.borrow_mut();
                    b.apple_next_pos = target_pos;
                    b.has_next_pos = true;
                }
                dino.target = Some(apple);
                dino.ops -= (dino.ops as f64 * 0.03).floor() as i32;
            } else {
                if !flag2 {
                    self.sh.warn("warning_missing_seed [Entities.Apple]".into());
                }
                dino.target = None;
            }
        }
        if flag || !dino.tail.is_empty() {
            let dinosaur = self.set_entity(old_pos.0, old_pos.1, "dinosaur");
            dinosaur.borrow_mut().drone_uid = uid;
            if !dino.tail.is_empty() && !flag {
                let last = dino.tail.back().unwrap().clone();
                let (lx, ly) = {
                    let mut b = last.borrow_mut();
                    b.is_in_snake = false;
                    (b.x, b.y)
                };
                self.remove_entity(lx, ly, true);
                dino.tail.pop_back();
            }
            dino.tail.push_front(dinosaur);
            let new_is_target = match (&dino.target, self.entity_or_null(new_pos.0, new_pos.1)) {
                (Some(t), Some(c)) => same(t, &c),
                (None, None) => true,
                _ => false,
            };
            if !dino.free_cells.is_empty() && dino.tail.len() > 1 && !new_is_target {
                dino.tail.back().unwrap().borrow_mut().can_move_to = true;
            }
        }
        let retarget = matches!(&dino.target, Some(t) if t.borrow().apple_next_pos == old_pos);
        if retarget {
            let mut target_pos2 = (0, 0);
            if self.try_choose_target(&dino.free_cells, &mut target_pos2, None) {
                dino.target.as_ref().unwrap().borrow_mut().apple_next_pos = target_pos2;
            }
        }
        let _ = num;
        let ops = dino.ops;
        if let Some(d) = self.drones[di].as_mut() {
            if d.hat.name == "dinosaur_hat" {
                d.hat.dino = Some(dino);
            }
        }
        ops
    }

    // ---- Drone ------------------------------------------------------------------------------
    fn dpos(&self, di: usize) -> (i32, i32) {
        let d = self.drones[di].as_ref().unwrap();
        (d.x, d.y)
    }
    fn entity_under_drone(&self, di: usize) -> Option<E> {
        let (x, y) = self.dpos(di);
        self.entity_at(x, y)
    }
    fn target_pos(&self, di: usize, dir: Option<u8>) -> (i32, i32) {
        let (x, y) = self.dpos(di);
        match dir {
            None => (x, y),
            Some(d) => self.wrap(x + DIRS[d as usize].0, y + DIRS[d as usize].1),
        }
    }

    fn drone_can_move(&self, di: usize, dir: u8) -> bool {
        let (x, y) = self.dpos(di);
        let v = (x + DIRS[dir as usize].0, y + DIRS[dir as usize].1);
        let v2 = self.wrap(v.0, v.1);
        let hat = self.drones[di].as_ref().unwrap().hat.name;
        if hat_prevents_wrapping(hat) && v2 != v {
            return false;
        }
        if let Some(entity) = self.entity_at(v2.0, v2.1) {
            let b = entity.borrow();
            let ok = match b.class {
                EC::Hedge | EC::Treasure => !b.walls.borrow()[reverse_dir(dir) as usize],
                EC::Dinosaur => b.can_move_to,
                _ => true,
            };
            if !ok {
                return false;
            }
        }
        if let Some(entity2) = self.entity_at(x, y) {
            let b = entity2.borrow();
            if is_hedge(b.class) && b.walls.borrow()[dir as usize] {
                return false;
            }
        }
        true
    }

    /// returns (moved, ops)
    fn drone_move(&mut self, di: usize, dir: u8) -> (bool, f64) {
        let (x, y) = self.dpos(di);
        let new_pos = (x + DIRS[dir as usize].0, y + DIRS[dir as usize].1);
        let v2 = self.wrap(new_pos.0, new_pos.1);
        if !self.drone_can_move(di, dir) {
            return (false, OPERATION_OPS);
        }
        let mut ops = -1.0;
        if self.drones[di].as_ref().unwrap().hat.dino.is_some() {
            ops = self.dino_on_move(di, (x, y), new_pos) as f64;
        }
        if ops <= 0.0 {
            ops = ACTION_OPS;
        }
        let d = self.drones[di].as_mut().unwrap();
        d.x = v2.0;
        d.y = v2.1;
        (true, ops)
    }

    fn drone_harvest(&mut self, di: usize) -> bool {
        let entity = match self.entity_under_drone(di) {
            Some(e) => e,
            None => return false,
        };
        // Cactus.Harvest reports the time since planting; every other plant reports zero
        let collection_duration = {
            let b = entity.borrow();
            if b.class == EC::Cactus { self.current_time - b.plant_time } else { 0 }
        };
        let items = self.entity_harvest(&entity);
        self.collect_items(items, collection_duration);
        self.drones[di].as_mut().unwrap().flight_height = 1;
        true
    }

    /// Drone.ChangeGround("soil")
    fn drone_till(&mut self, di: usize) {
        let (x, y) = self.dpos(di);
        let ground = self.cells[self.idx(x, y)].ground;
        if ground != "grassland" && ground != "soil" {
            return;
        }
        let under_hedge = |sim: &Sim| matches!(sim.entity_at(x, y), Some(e) if is_hedge(e.borrow().class));
        if !under_hedge(self) {
            self.remove_entity(x, y, false);
        }
        let is_over = matches!(self.entity_at(x, y), Some(e) if e.borrow().so.name == "soil") || ground == "soil";
        if is_over {
            self.set_ground(x, y, "grassland");
            if !under_hedge(self) {
                self.set_entity(x, y, "grass");
            }
        } else {
            self.set_ground(x, y, "soil");
        }
    }

    fn drone_plant(&mut self, di: usize, name: &'static str) -> R<bool> {
        let (x, y) = self.dpos(di);
        let so = entity_so(name);
        if let Some(e) = self.entity_at(x, y) {
            if !e.borrow().so.overplant {
                return Ok(false);
            }
        }
        let ground = self.cells[self.idx(x, y)].ground;
        // EntitySO.CanBePlacedOn
        let can_place = so.can_be_planted && !so.placeable_on.is_empty() && {
            let all = so.placeable_on[0] == "all";
            let listed = so.placeable_on.contains(&ground);
            all != listed
        };
        if !can_place {
            self.sh.warn(format!("warning_cant_plant_on_ground [Entities.{}, {}]", to_upper_snake(name), ground));
            return Ok(false);
        }
        if !self.is_unlocked(name) {
            return Err(err("error_missing_x_unlock", &[format!("Entities.{}", to_upper_snake(name))]));
        }
        if entity_class(so).is_none() {
            return Err(format!("Entities.{} belongs to the mining DLC, which is not ported", to_upper_snake(name)));
        }
        let num = (self.num_unlocked(so.yield_upgrade) - 1).max(0);
        let cost = cost_block(so.cost, (1i32 << num).max(1) as f64);
        if !self.items_remove(&cost) {
            self.sh.warn(format!("warning_missing_seed [Entities.{}]", to_upper_snake(name)));
            return Ok(false);
        }
        self.set_entity(x, y, name);
        self.drones[di].as_mut().unwrap().flight_height = 1;
        Ok(true)
    }

    // ---- Execution --------------------------------------------------------------------------
    fn add_program_state(&mut self, drone_id: usize, program: Vm, op_count: f64) -> StRef {
        let st = Rc::new(RefCell::new(PState::new(op_count, &mut self.random_random, drone_id as i32, self.sh.clone())));
        register_builtins(&st.borrow().module_state.global_scope.clone());
        st.borrow_mut().program = Some(Box::new(program));
        let ex = self.execution.as_mut().unwrap();
        assert!(drone_id < MAX_DRONE_SLOTS, "more than {} drones", MAX_DRONE_SLOTS);
        ex.hot[drone_id] = Hot {
            op_count,
            target_op_count: 0.0,
            last_consumed_op_count: op_count,
            awaited_drone_id: -1,
            resumes: 0,
            se: SE_NONE,
            present: true,
        };
        st.borrow_mut().hot = &mut ex.hot[drone_id] as *mut Hot;
        if drone_id >= ex.states.len() {
            ex.states.push(Some(st.clone()));
        } else {
            ex.states[drone_id] = Some(st.clone());
        }
        st
    }

    /// new Execution(sim, syntaxTree, id) + Simulation.StartProgramExecution
    fn start_program_execution(&mut self, tree: Rc<Node>) {
        self.execution = Some(Execution {
            states: Vec::new(),
            hot: vec![HOT_EMPTY; MAX_DRONE_SLOTS],
            main_state: None,
            global_op_count: 0.0,
            next_execution_time: self.current_time,
            stopped: false,
        });
        let st = self.add_program_state(0, Vm::main(&tree), 0.0);
        self.execution.as_mut().unwrap().main_state = Some(st);
        self.paused = false;
        self.finished = false;
    }

    fn min_op_count(&self, default: f64) -> f64 {
        let ex = self.execution.as_ref().unwrap();
        let hot = &ex.hot[..ex.states.len()];
        let mut m = [f64::INFINITY; 4];
        let mut any = false;
        let mut chunks = hot.chunks_exact(4);
        for c in &mut chunks {
            for k in 0..4 {
                let h = &c[k];
                let run = h.present & (h.awaited_drone_id < 0);
                any |= run;
                m[k] = m[k].min(if run { h.op_count } else { f64::INFINITY });
            }
        }
        for h in chunks.remainder() {
            let run = h.present & (h.awaited_drone_id < 0);
            any |= run;
            m[0] = m[0].min(if run { h.op_count } else { f64::INFINITY });
        }
        if any { m[0].min(m[1]).min(m[2].min(m[3])) } else { default }
    }

    /// Not in the game: a shortcut with the same outcome. Drones spinning in
    /// `while get_time() < x: pass` take two ops per pass and affect nothing, yet the loop below
    /// would visit every pass of every one of them. This moves each of them straight to the pass
    /// it would have reached by the time anything else can happen: another drone's next side
    /// effect, the first pass whose clock reading ends a wait, or the end of this Execute call.
    /// `base` is the op count the current time stands for.
    fn skip_busy_waits(&mut self, num: f64, base: f64) {
        if self.paused {
            return;
        }
        let mut limit = num - 1.0;
        // each skipped drone with its ops per pass
        let mut waiting = std::mem::take(&mut self.waiting_scratch);
        waiting.clear();
        let ex = self.execution.as_ref().unwrap();
        for si in 0..ex.states.len() {
            let h = &ex.hot[si];
            if !h.present || h.awaited_drone_id >= 0 {
                continue;
            }
            // only a drone asking for the time or an item count can be in a skippable wait
            if h.se != SE_GET_TIME && h.se != SE_NUM_ITEMS {
                limit = limit.min(h.op_count);
                continue;
            }
            let b = ex.states[si].as_ref().unwrap().borrow();
            // `while num_items(i) < x: pass` that last read the count it would read now: every
            // pass until another drone's next side effect reads the same count and stays in the
            // loop. (The count changes only through side effects and timers, and timers run
            // between Execute calls.)
            if let (SE::NumItems(item), true, Some((_, v)), Some(p)) =
                (&b.current_side_effect, b.spin_loop, b.spin_read, b.spin_period)
            {
                if p > 0.0 && self.items[item_id(item)] == v {
                    drop(b);
                    waiting.push((si, p));
                    continue;
                }
            }
            let deadline = match (&b.current_side_effect, b.wait_deadline) {
                (SE::GetTime, Some(d)) => d,
                _ => {
                    limit = limit.min(b.h().op_count);
                    continue;
                }
            };
            // the first pass of this drone that reads a time at or past its deadline
            let reads = |ops: f64| dur_seconds(self.current_time + dur_mul(self.op_duration, ops - base));
            let c = b.h().op_count;
            // The clock reads origin + op_duration * ops exactly (whole nanoseconds times whole op
            // counts), so that first pass stays the same while the deadline, the origin and the op
            // duration do: the passes before it at this drone's parity all read too early.
            let origin = self.current_time - dur_mul(self.op_duration, base);
            let key = (deadline.to_bits(), origin, self.op_duration);
            let wc = b.wait_cache;
            if (wc.0, wc.1, wc.2) == key && c <= wc.3 && ((wc.3 - c) * 0.5).fract() == 0.0 {
                limit = limit.min(wc.3);
                drop(b);
                waiting.push((si, 2.0));
                continue;
            }
            let estimate = (deadline * 1e9 - self.current_time as f64) / self.op_duration as f64 + base - c;
            let mut j = (estimate / 2.0).ceil().max(0.0);
            if !j.is_finite() {
                limit = limit.min(c);
                continue;
            }
            while j > 0.0 && !(reads(c + 2.0 * (j - 1.0)) < deadline) {
                j -= 1.0;
            }
            while reads(c + 2.0 * j) < deadline {
                j += 1.0;
            }
            limit = limit.min(c + 2.0 * j);
            drop(b);
            ex.states[si].as_ref().unwrap().borrow_mut().wait_cache = (key.0, key.1, key.2, c + 2.0 * j);
            waiting.push((si, 2.0));
        }
        for (si, p) in waiting.iter() {
            let mut b = ex.states[*si].as_ref().unwrap().borrow_mut();
            if b.h().op_count < limit {
                b.h().op_count += p * ((limit - b.h().op_count) / p).ceil();
                // the skipped passes read the same count, the last of them one pass ago
                let c = b.h().op_count;
                if let Some((at, _)) = b.spin_read.as_mut() {
                    *at = c - p;
                }
            }
        }
        self.waiting_scratch = waiting;
    }

    /// Execution.Execute
    fn execute(&mut self, target_run_time: i64) {
        let num = (self.execution.as_ref().unwrap().global_op_count
            + f64::min(199.0, target_run_time as f64 / self.op_duration as f64))
        .floor();
        loop {
            let global_op_count = match &self.execution {
                Some(ex) => ex.global_op_count,
                None => return,
            };
            {
                // Running a drone's program touches only its own state, never the drone list.
                let ex = self.execution.as_ref().unwrap();
                let n = ex.states.len();
                if n <= 64 {
                    let mut mask = 0u64;
                    for (i, h) in ex.hot[..n].iter().enumerate() {
                        let r = h.present & (h.se == SE_NONE) & !(h.op_count > num) & (h.awaited_drone_id < 0);
                        mask |= (r as u64) << i;
                    }
                    while mask != 0 {
                        let i = mask.trailing_zeros() as usize;
                        mask &= mask - 1;
                        perform_execution_step(ex.states[i].as_ref().unwrap(), num);
                    }
                } else {
                    for i in 0..n {
                        let h = &ex.hot[i];
                        if h.present && h.se == SE_NONE && !(h.op_count > num) && h.awaited_drone_id < 0 {
                            perform_execution_step(ex.states[i].as_ref().unwrap(), num);
                        }
                    }
                }
            }
            self.skip_busy_waits(num, global_op_count);
            let g = self.min_op_count(num);
            self.execution.as_mut().unwrap().global_op_count = g;

            let mut num2 = 0.0;
            // min(num, every running drone's op count): min_op_count just took that minimum
            // (or returned num when no drone is running)
            let num3 = num.min(g);
            self.add_ops_to_current_time(num3 - global_op_count);
            if !self.paused {
                {
                    let ex = self.execution.as_mut().unwrap();
                    let n = ex.states.len();
                    for h in ex.hot[..n].iter_mut() {
                        // PState::consume_ops (an empty slot keeps op == last, so adds exactly 0)
                        num2 += h.op_count - h.last_consumed_op_count;
                        h.last_consumed_op_count = h.op_count;
                    }
                }
                let mut due_mask = 0u64;
                let masked = {
                    let ex = self.execution.as_ref().unwrap();
                    let n = ex.states.len();
                    if n <= 64 {
                        let g = ex.global_op_count;
                        for (i, h) in ex.hot[..n].iter().enumerate() {
                            let d = h.present & (h.awaited_drone_id < 0) & (h.se != SE_NONE) & !(h.op_count > g);
                            due_mask |= (d as u64) << i;
                        }
                        true
                    } else {
                        false
                    }
                };
                let mut num6 = 0;
                loop {
                    let ex = match &self.execution {
                        Some(ex) => ex,
                        None => return,
                    };
                    if masked {
                        if due_mask == 0 || ex.global_op_count > num {
                            break;
                        }
                        num6 = due_mask.trailing_zeros() as usize;
                        due_mask &= due_mask - 1;
                    } else if num6 >= ex.states.len() || ex.global_op_count > num {
                        break;
                    }
                    let due = masked || {
                        let h = &ex.hot[num6];
                        h.present && h.awaited_drone_id < 0 && h.se != SE_NONE && !(h.op_count > ex.global_op_count)
                    };
                    if due {
                        let s = ex.states[num6].clone().unwrap();
                        if let Err(e) = self.apply_side_effect(num6) {
                            {
                                let mut b = s.borrow_mut();
                                b.current_execute_exception = Some(e);
                                b.set_se(SE::Error);
                            }
                            let _ = self.apply_side_effect(num6);
                        }
                        let mut b = s.borrow_mut();
                        num2 += b.consume_ops();
                        b.set_se(SE::None);
                    }
                    num6 += 1;
                }
                self.used_power += num2 / 200.0 / 30.0;
            }
            if self.execution.is_none() {
                return;
            }
            let g = self.min_op_count(num);
            let ex = self.execution.as_mut().unwrap();
            ex.global_op_count = g;
            ex.next_execution_time = self.current_time + dur_mul(self.op_duration, g - num3);
            self.add_ops_to_current_time(g.min(num) - num3);
            if g > num || self.paused {
                break;
            }
        }
    }

    fn state(&self, drone_id: usize) -> StRef {
        self.execution.as_ref().unwrap().states[drone_id].clone().unwrap()
    }

    /// Execution.ApplySideEffect
    fn apply_side_effect(&mut self, drone_id: usize) -> R<f64> {
        let st = self.state(drone_id);
        let se = st.borrow().current_side_effect.clone();
        let mut ops = 0.0;
        let mut flag = true;
        let mut ret: Option<V> = None;
        match se {
            SE::None => {}
            SE::Harvest => {
                let r = self.drone_harvest(drone_id);
                ret = Some(V::Bool(r));
                ops = if r { ACTION_OPS } else { OPERATION_OPS };
            }
            SE::CanHarvest => {
                let r = match self.entity_under_drone(drone_id) {
                    Some(e) => self.harvestable(&e),
                    None => false,
                };
                ret = Some(V::Bool(r));
                ops = OPERATION_OPS;
            }
            SE::Swap(dir) => {
                let (x, y) = self.dpos(drone_id);
                let r = self.swap(x, y, dir);
                if !r {
                    let (x2, y2) = (x + DIRS[dir as usize].0, y + DIRS[dir as usize].1);
                    self.sh.warn(if !self.in_bounds(x2, y2) { "warning_failed_swap_wrap".into() } else { "warning_failed_swap_unswappable".into() });
                }
                ret = Some(V::Bool(r));
                ops = if r { ACTION_OPS } else { OPERATION_OPS };
            }
            SE::Plant(name) => {
                let r = entity_so(name).can_be_planted && self.drone_plant(drone_id, name)?;
                ret = Some(V::Bool(r));
                ops = if r { ACTION_OPS } else { OPERATION_OPS };
            }
            SE::Move(dir) => {
                let (r, o) = self.drone_move(drone_id, dir);
                ret = Some(V::Bool(r));
                ops = o;
            }
            SE::CanMove(dir) => {
                ret = Some(V::Bool(self.drone_can_move(drone_id, dir)));
                ops = OPERATION_OPS;
            }
            SE::Till => {
                self.drone_till(drone_id);
                ret = Some(V::None);
                ops = ACTION_OPS;
            }
            SE::GetPosX => {
                ret = Some(V::Num(self.dpos(drone_id).0 as f64));
                ops = OPERATION_OPS;
            }
            SE::GetPosY => {
                ret = Some(V::Num(self.dpos(drone_id).1 as f64));
                ops = OPERATION_OPS;
            }
            SE::GetPosZ => {
                ret = Some(V::Num(0.0));
                ops = OPERATION_OPS;
            }
            SE::GetWorldSize => {
                ret = Some(V::Num(self.wy as f64));
                ops = OPERATION_OPS;
            }
            SE::GetEntityType(dir) => {
                let (x, y) = self.target_pos(drone_id, dir);
                ret = Some(match self.entity_at(x, y) {
                    Some(e) => V::Const(NS_ENTITIES, e.borrow().so.name),
                    None => V::None,
                });
                ops = OPERATION_OPS;
            }
            SE::GetGroundType(dir) => {
                let (x, y) = self.target_pos(drone_id, dir);
                ret = Some(V::Const(NS_GROUNDS, self.cells[self.idx(x, y)].ground));
                ops = OPERATION_OPS;
            }
            SE::UseItem(item, num3) => {
                let id = item_id(item);
                if self.items[id] < num3 as f64 {
                    self.sh.warn(format!("warning_no_item_to_use [Items.{}]", to_upper_snake(item)));
                    ret = Some(V::Bool(false));
                    ops = OPERATION_OPS;
                } else {
                    let mut flag4 = false;
                    let mut use_action_ticks = false;
                    let (x, y) = self.dpos(drone_id);
                    let entity = self.entity_at(x, y);
                    match item {
                        "water" => {
                            let w = self.cells[self.idx(x, y)].water_volume;
                            self.set_water_volume(x, y, w + 0.25 * num3 as f64);
                            flag4 = true;
                            use_action_ticks = true;
                        }
                        "fertilizer" => {
                            if let Some(e) = &entity {
                                let ok = {
                                    let b = e.borrow();
                                    is_growable(b.class) && b.so.can_be_weird
                                };
                                if ok {
                                    self.fertilize(e, num3);
                                    flag4 = true;
                                }
                            }
                            use_action_ticks = flag4;
                        }
                        "weird_substance" => {
                            if let Some(e) = &entity {
                                let (class, can_be_weird) = {
                                    let b = e.borrow();
                                    (b.class, b.so.can_be_weird)
                                };
                                let mazes = self.is_unlocked("mazes");
                                if class == EC::Bush && mazes {
                                    let num4 = 1 << (self.num_unlocked("mazes") - 1);
                                    if num3 % num4 != 0 {
                                        self.sh.warn("warning_weird_substance_not_divisible".into());
                                    }
                                    let num5 = num3 / num4;
                                    if num5 < 1 {
                                        self.toggle_weird(e);
                                    } else {
                                        self.generate_hedge_maze(e, num5);
                                        flag4 = true;
                                        use_action_ticks = true;
                                    }
                                } else if class == EC::Treasure && mazes {
                                    let num6 = num3 / (1 << (self.num_unlocked("mazes") - 1));
                                    if num6 >= 1 {
                                        let (r, u) = self.reposition_treasure(e, num6);
                                        flag4 = r;
                                        use_action_ticks = u;
                                    }
                                } else if is_growable(class) && can_be_weird {
                                    self.toggle_weird(e);
                                    flag4 = true;
                                    use_action_ticks = true;
                                }
                            }
                        }
                        "dynamite" => return Err("use_item(Items.Dynamite) belongs to the mining DLC, which is not ported".into()),
                        _ => {}
                    }
                    ret = Some(V::Bool(flag4));
                    if flag4 {
                        self.items[id] -= num3 as f64;
                    }
                    ops = if use_action_ticks { ACTION_OPS } else { OPERATION_OPS };
                }
            }
            SE::GetWater => {
                let (x, y) = self.dpos(drone_id);
                ret = Some(V::Num(self.cells[self.idx(x, y)].water_volume));
                ops = OPERATION_OPS;
            }
            SE::ChangeHat(hat) => {
                if !self.is_unlocked(hat) {
                    return Err(err("error_missing_x_unlock", &[format!("Hats.{}", to_upper_snake(hat))]));
                }
                self.drones[drone_id].as_mut().unwrap().flight_height = 1;
                ops = ACTION_OPS;
                st.borrow_mut().module_state.return_value = V::None;
                self.drone_change_hat(drone_id, create_hat(hat, false))?;
                ret = Some(V::None);
            }
            SE::NumItems(item) => {
                let v = self.items[item_id(item)];
                ret = Some(V::Num(v));
                ops = OPERATION_OPS;
                let mut b = st.borrow_mut();
                if b.spin_loop {
                    let c = b.h().op_count;
                    if let Some((prev, _)) = b.spin_read {
                        b.spin_period = Some(c - prev);
                    }
                    b.spin_read = Some((c, v));
                }
            }
            SE::GetCost(thing, level) => {
                let block = match &thing {
                    V::Const(NS_UNLOCKS, name) => {
                        let so = unlock_so(name).unwrap();
                        let n = match &level {
                            Some(l) => l.num().unwrap_or(-1.0) as i32,
                            None => -1,
                        };
                        self.get_unlock_cost(so, n)
                    }
                    V::Const(_, name) => {
                        let so = entity_so(name);
                        if so.yield_upgrade.is_empty() {
                            cost_block(so.cost, 1.0)
                        } else {
                            let num12 = (self.num_unlocked(so.yield_upgrade) - 1).max(0);
                            cost_block(so.cost, (1i32 << num12) as f64)
                        }
                    }
                    _ => empty_items(),
                };
                // BuiltinFunctions.ItemsToNewDict
                let mut d = DMap::new(false);
                for (i, n) in block.iter().enumerate() {
                    if *n > 0.0 {
                        let k = V::Const(NS_ITEMS, ITEM_NAMES[i]);
                        d.put(to_key(&k)?, k, V::Num(*n));
                    }
                }
                ret = Some(V::Dict(Rc::new(RefCell::new(d))));
                ops = OPERATION_OPS;
            }
            SE::Clear => {
                self.remove_spawned_drones();
                self.clear_grid();
                if let Some(Some(d)) = self.drones.get_mut(0) {
                    d.flight_height = 1;
                    d.x = 0;
                    d.y = 0;
                }
                let g = {
                    let ex = self.execution.as_mut().unwrap();
                    ex.main_state = Some(st.clone());
                    ex.states = vec![Some(st.clone())];
                    ex.global_op_count
                };
                let mut b = st.borrow_mut();
                b.drone_id = 0;
                if b.h().awaited_drone_id >= 0 {
                    b.h().awaited_drone_id = -1;
                    b.h().op_count = g;
                }
                drop(b);
                ops = ACTION_OPS;
                ret = Some(V::None);
            }
            SE::GetCompanion => {
                ret = Some(match self.entity_under_drone(drone_id) {
                    Some(e) => {
                        let b = e.borrow();
                        if is_growable(b.class) && b.so.companion {
                            V::Tuple(Rc::new(vec![
                                V::Const(NS_ENTITIES, b.companion_type),
                                tuple2(b.companion_pos.0 as f64, b.companion_pos.1 as f64),
                            ]))
                        } else {
                            V::None
                        }
                    }
                    None => V::None,
                });
                ops = OPERATION_OPS;
            }
            SE::Unlock(name) => {
                let r = self.unlock_or_upgrade(unlock_so(name).unwrap());
                ret = Some(V::Bool(r));
                ops = if r { ACTION_OPS } else { OPERATION_OPS };
            }
            SE::NumUnlocked(thing) => {
                if let V::Const(_, name) = &thing {
                    ret = Some(V::Num(self.num_unlocked(name) as f64));
                }
                ops = OPERATION_OPS;
            }
            SE::Measure(dir) => {
                let (x, y) = self.target_pos(drone_id, dir);
                let v = match self.entity_at(x, y) {
                    Some(e) => self.entity_measure(&e),
                    None => None,
                };
                ret = Some(v.unwrap_or(V::None));
                ops = OPERATION_OPS;
            }
            SE::SetExecutionSpeed(num) => {
                let m = self.max_speed_factor();
                if num.is_nan() || num > m || num < 0.1 {
                    self.change_execution_speed(m);
                } else {
                    self.change_execution_speed(num);
                }
                ret = Some(V::None);
                ops = ACTION_OPS;
            }
            SE::SetWorldSize(v) => {
                let num13 = v as i32;
                if num13 != self.wy && (num13 > 2 || self.size_limit > 0) {
                    for d in self.drones.iter_mut().flatten() {
                        d.flight_height = 1;
                        d.x = 0;
                        d.y = 0;
                    }
                    self.set_size_limit(num13);
                }
                ret = Some(V::None);
                ops = ACTION_OPS;
            }
            SE::GetTime => {
                ret = Some(V::Num(dur_seconds(self.current_time)));
                ops = 0.0;
            }
            SE::SpawnDrone(obj) => {
                let num9 = self.execution.as_ref().unwrap().states.iter().flatten().count() as i32;
                if num9 >= self.max_drones() {
                    ret = Some(V::None);
                    ops = OPERATION_OPS;
                } else {
                    let mut copies = Copies::new();
                    let py_function = match deep_copy(&obj[0], &mut copies) {
                        V::Func(f) => f,
                        _ => return Err("error_spawn_drone_builtin".into()),
                    };
                    let num11 = self.add_drone(drone_id)?;
                    let function_node = py_function.syntax_tree.clone().unwrap();
                    let list2: Vec<V> = obj[1..].iter().map(|a| deep_copy(a, &mut copies)).collect();
                    let g = self.execution.as_ref().unwrap().global_op_count;
                    let fnode = function_node.clone();
                    let new_state =
                        self.add_program_state(num11, Vm::spawned(&fnode, list2), g + ACTION_OPS);
                    let vars = match &function_node.kind {
                        NK::Function { vars, .. } => vars.clone(),
                        _ => Vec::new(),
                    };
                    let scope = new_scope(Some(function_node.clone()), py_function.parent_scope.clone(), &vars);
                    let handle = Rc::new(DroneHandle {
                        id: num11 as i32,
                        generation: self.drone_generation,
                        return_value: RefCell::new(None),
                    });
                    {
                        let mut b = new_state.borrow_mut();
                        b.module_state.call_stack.push(scope);
                        b.drone_handle = Some(handle.clone());
                        b.current_executing_node = st.borrow().current_executing_node;
                    }
                    ret = Some(V::Handle(handle));
                    ops = ACTION_OPS;
                }
            }
            SE::NumDrones => {
                ret = Some(V::Num(self.execution.as_ref().unwrap().states.iter().flatten().count() as f64));
                ops = OPERATION_OPS;
            }
            SE::MaxDrones => {
                ret = Some(V::Num(self.max_drones() as f64));
                ops = OPERATION_OPS;
            }
            SE::Await(handle) => {
                let done = handle.return_value.borrow().clone();
                match done {
                    Some(v) => {
                        ret = Some(deep_copy(&v, &mut Copies::new()));
                        ops = OPERATION_OPS;
                    }
                    None => {
                        st.borrow_mut().h().awaited_drone_id = handle.id;
                        ops = OPERATION_OPS;
                    }
                }
            }
            SE::HasFinished(handle) => {
                ret = Some(V::Bool(handle.return_value.borrow().is_some()));
                ops = OPERATION_OPS;
            }
            SE::Terminated => {
                let value = st.borrow().module_state.return_value.clone();
                let g = self.execution.as_ref().unwrap().global_op_count;
                let states = self.execution.as_ref().unwrap().states.clone();
                for other in states.iter().flatten() {
                    if other.borrow().h().awaited_drone_id == drone_id as i32 {
                        let copy = deep_copy(&value, &mut Copies::new());
                        let mut b = other.borrow_mut();
                        b.h().awaited_drone_id = -1;
                        b.h().op_count = g;
                        b.module_state.return_value = copy;
                    }
                }
                if let Some(h) = &st.borrow().drone_handle {
                    *h.return_value.borrow_mut() = Some(value.clone());
                }
                let all_done = {
                    let ex = self.execution.as_mut().unwrap();
                    if matches!(&ex.main_state, Some(m) if Rc::ptr_eq(m, &st)) {
                        ex.main_state = None;
                    }
                    ex.states[drone_id] = None;
                    let h = &mut ex.hot[drone_id];
                    h.present = false;
                    h.last_consumed_op_count = h.op_count;
                    ex.states.iter().all(|s| s.is_none())
                };
                if all_done {
                    self.stop_program_execution();
                } else {
                    self.remove_drone(drone_id);
                    let main = self.main_drone_id;
                    let ex = self.execution.as_mut().unwrap();
                    ex.main_state = ex.states.get(main).cloned().flatten();
                }
            }
            SE::Error => {
                let (msg, node) = {
                    let b = st.borrow();
                    (b.current_execute_exception.clone().unwrap_or_else(|| "Unexpected error".into()), b.current_executing_node)
                };
                let place = match unsafe { node.as_ref() } {
                    Some(n) => format!("{}.py line {}", n.file.name, n.file.line_of(n.word_start)),
                    None => "?".into(),
                };
                self.error = Some(format!("{} (drone {}): {}", place, drone_id, msg));
                self.has_error = true;
                self.paused = true;
            }
            SE::DoAFlip | SE::PetThePiggy => {
                ret = Some(V::None);
                ops = (1.0 / dur_seconds(self.op_duration)).floor();
                flag = false;
            }
            SE::Print(s) => {
                self.sh.log(&s);
                ret = Some(V::None);
                ops = (1.0 / dur_seconds(self.op_duration)).floor();
                flag = false;
            }
            SE::NotPorted(name) => {
                return Err(format!("{}() is not ported (mining DLC, leaderboards and simulate are out of scope)", name));
            }
        }
        let mut b = st.borrow_mut();
        if let Some(v) = ret {
            b.module_state.return_value = v;
        }
        if flag {
            b.h().op_count += ops;
        } else {
            b.add_and_consume_ops(ops);
        }
        Ok(ops)
    }
}

// ---------------------------------------------------------------------------------------------
// Harness: save.json, command line, frame loop, report
// ---------------------------------------------------------------------------------------------
#[derive(Debug, Clone)]
enum Json {
    Null,
    Bool(bool),
    Num(f64),
    Str(String),
    Arr(Vec<Json>),
    Obj(Vec<(String, Json)>),
}

impl Json {
    fn get(&self, key: &str) -> Option<&Json> {
        match self {
            Json::Obj(o) => o.iter().find(|(k, _)| k == key).map(|(_, v)| v),
            _ => None,
        }
    }
    fn arr(&self) -> &[Json] {
        match self {
            Json::Arr(a) => a,
            _ => &[],
        }
    }
}

fn parse_json(text: &str) -> R<Json> {
    let c: Vec<char> = text.chars().collect();
    let mut p = 0usize;
    fn ws(c: &[char], p: &mut usize) {
        while *p < c.len() && c[*p].is_whitespace() {
            *p += 1;
        }
    }
    fn value(c: &[char], p: &mut usize) -> R<Json> {
        ws(c, p);
        if *p >= c.len() {
            return Err("unexpected end of json".into());
        }
        match c[*p] {
            '{' => {
                *p += 1;
                let mut out = Vec::new();
                loop {
                    ws(c, p);
                    if c[*p] == '}' {
                        *p += 1;
                        break;
                    }
                    let k = match value(c, p)? {
                        Json::Str(s) => s,
                        _ => return Err("json object key is not a string".into()),
                    };
                    ws(c, p);
                    *p += 1; // ':'
                    out.push((k, value(c, p)?));
                    ws(c, p);
                    if c[*p] == ',' {
                        *p += 1;
                    }
                }
                Ok(Json::Obj(out))
            }
            '[' => {
                *p += 1;
                let mut out = Vec::new();
                loop {
                    ws(c, p);
                    if c[*p] == ']' {
                        *p += 1;
                        break;
                    }
                    out.push(value(c, p)?);
                    ws(c, p);
                    if c[*p] == ',' {
                        *p += 1;
                    }
                }
                Ok(Json::Arr(out))
            }
            '"' => {
                *p += 1;
                let mut s = String::new();
                while c[*p] != '"' {
                    if c[*p] == '\\' {
                        *p += 1;
                        match c[*p] {
                            'n' => s.push('\n'),
                            't' => s.push('\t'),
                            'r' => s.push('\r'),
                            'u' => {
                                let hex: String = c[*p + 1..*p + 5].iter().collect();
                                s.push(char::from_u32(u32::from_str_radix(&hex, 16).unwrap_or(63)).unwrap_or('?'));
                                *p += 4;
                            }
                            other => s.push(other),
                        }
                    } else {
                        s.push(c[*p]);
                    }
                    *p += 1;
                }
                *p += 1;
                Ok(Json::Str(s))
            }
            't' => {
                *p += 4;
                Ok(Json::Bool(true))
            }
            'f' => {
                *p += 5;
                Ok(Json::Bool(false))
            }
            'n' => {
                *p += 4;
                Ok(Json::Null)
            }
            _ => {
                let start = *p;
                while *p < c.len() && (c[*p].is_ascii_digit() || "+-.eE".contains(c[*p])) {
                    *p += 1;
                }
                let s: String = c[start..*p].iter().collect();
                s.parse::<f64>().map(Json::Num).map_err(|_| format!("bad json number {s}"))
            }
        }
    }
    value(&c, &mut p)
}

/// Every run simulates this long. A script whose cycle is too slow to harvest the reported item
/// MIN_HARVESTS times in that window keeps running until it has, up to MAX_RUN_SECONDS, because
/// the steady-state rate needs at least two harvests to measure the time between them.
const RUN_SECONDS: f64 = 60.0;
const MIN_HARVESTS: usize = 3;
const MAX_RUN_SECONDS: f64 = 600.0;
/// Real (wall-clock) seconds one run may take before it is stopped with an error. Slow runs make
/// a variant search crawl, so the script being run has to be made cheaper to simulate.
const WALL_LIMIT_SECONDS: f64 = 10.0;

// ---- Leaderboards ------------------------------------------------------------------------------
// From the game's LeaderboardSO assets (resources.assets) and BuiltinFunctions.LeaderboardRun /
// MainSim.StartLeaderboard / MainSim.LeaderboardExecutionFinished in Core.dll.

#[derive(Clone, Copy, PartialEq)]
enum LbKind {
    /// LeaderboardType.reset: start from nothing, succeed by unlocking the leaderboard again
    Reset,
    /// LeaderboardType.farm_resources: everything unlocked, succeed by holding the goal items
    Farm,
}

struct Lb {
    name: &'static str,
    kind: LbKind,
    single_drone: bool,
    /// needs the mining DLC, which this simulator does not port
    dlc: bool,
    start: &'static [(&'static str, f64)],
    goal: &'static [(&'static str, f64)],
}

static LEADERBOARDS: &[Lb] = &[
    Lb { name: "bamboo", kind: LbKind::Farm, single_drone: false, dlc: true, start: &[("power", 1e9), ("rice", 1e9)], goal: &[("bamboo", 500000000.0)] },
    Lb { name: "bamboo_single", kind: LbKind::Farm, single_drone: true, dlc: true, start: &[("power", 1e9), ("rice", 1e9)], goal: &[("bamboo", 25000000.0)] },
    Lb { name: "cactus", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("pumpkin", 1e9), ("power", 1e9)], goal: &[("cactus", 33554432.0)] },
    Lb { name: "cactus_single", kind: LbKind::Farm, single_drone: true, dlc: false, start: &[("pumpkin", 1e9), ("power", 1e9)], goal: &[("cactus", 131072.0)] },
    Lb { name: "carrots", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("power", 1e9), ("hay", 1e9), ("wood", 1e9)], goal: &[("carrot", 2000000000.0)] },
    Lb { name: "carrots_single", kind: LbKind::Farm, single_drone: true, dlc: false, start: &[("power", 1e9), ("hay", 1e9), ("wood", 1e9)], goal: &[("carrot", 100000000.0)] },
    Lb { name: "dinosaur", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("cactus", 1e9), ("power", 1e9)], goal: &[("bone", 33488928.0)] },
    Lb { name: "dynamite", kind: LbKind::Farm, single_drone: false, dlc: true, start: &[("power", 1e9)], goal: &[("dynamite", 10000000.0)] },
    Lb { name: "dynamite_single", kind: LbKind::Farm, single_drone: true, dlc: true, start: &[("power", 1e9)], goal: &[("dynamite", 100000.0)] },
    Lb { name: "fastest_reset", kind: LbKind::Reset, single_drone: false, dlc: false, start: &[], goal: &[] },
    Lb { name: "fastest_underground_reset", kind: LbKind::Reset, single_drone: false, dlc: true, start: &[], goal: &[] },
    Lb { name: "hay", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("power", 1e9)], goal: &[("hay", 2000000000.0)] },
    Lb { name: "hay_single", kind: LbKind::Farm, single_drone: true, dlc: false, start: &[("power", 1e9)], goal: &[("hay", 100000000.0)] },
    Lb { name: "maze", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("weird_substance", 1e9), ("power", 1e9)], goal: &[("gold", 9863168.0)] },
    Lb { name: "maze_single", kind: LbKind::Farm, single_drone: true, dlc: false, start: &[("weird_substance", 1e9), ("power", 1e9)], goal: &[("gold", 616448.0)] },
    Lb { name: "mushrooms", kind: LbKind::Farm, single_drone: false, dlc: true, start: &[("power", 1e9)], goal: &[("mushroom", 240000.0)] },
    Lb { name: "mushrooms_single", kind: LbKind::Farm, single_drone: true, dlc: true, start: &[("power", 1e9)], goal: &[("mushroom", 30000.0)] },
    Lb { name: "ores", kind: LbKind::Farm, single_drone: false, dlc: true, start: &[("power", 1e9)], goal: &[("quartz", 20000.0)] },
    Lb { name: "ores_single", kind: LbKind::Farm, single_drone: true, dlc: true, start: &[("power", 1e9)], goal: &[("quartz", 4000.0)] },
    Lb { name: "pumpkins", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("carrot", 1e9), ("power", 1e9)], goal: &[("pumpkin", 200000000.0)] },
    Lb { name: "pumpkins_single", kind: LbKind::Farm, single_drone: true, dlc: false, start: &[("carrot", 1e9), ("power", 1e9)], goal: &[("pumpkin", 10000000.0)] },
    Lb { name: "pyramids", kind: LbKind::Farm, single_drone: false, dlc: true, start: &[], goal: &[("power", 150000.0)] },
    Lb { name: "pyramids_single", kind: LbKind::Farm, single_drone: true, dlc: true, start: &[], goal: &[("power", 30000.0)] },
    Lb { name: "rice", kind: LbKind::Farm, single_drone: false, dlc: true, start: &[("power", 1e9)], goal: &[("rice", 2000000.0)] },
    Lb { name: "rice_single", kind: LbKind::Farm, single_drone: true, dlc: true, start: &[("power", 1e9)], goal: &[("rice", 100000.0)] },
    Lb { name: "sunflowers", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("carrot", 1e9)], goal: &[("power", 100000.0)] },
    Lb { name: "sunflowers_single", kind: LbKind::Farm, single_drone: true, dlc: false, start: &[("carrot", 1e9)], goal: &[("power", 10000.0)] },
    Lb { name: "treasure_map", kind: LbKind::Farm, single_drone: true, dlc: true, start: &[("power", 1e9)], goal: &[("gold", 115000.0)] },
    Lb { name: "wood", kind: LbKind::Farm, single_drone: false, dlc: false, start: &[("power", 1e9)], goal: &[("wood", 10000000000.0)] },
    Lb { name: "wood_single", kind: LbKind::Farm, single_drone: true, dlc: false, start: &[("power", 1e9)], goal: &[("wood", 500000000.0)] },
];

/// BuiltinFunctions.resetUnlocks: what every leaderboard run (and a fresh reset) starts with
static RESET_UNLOCKS: &[&str] = &[
    "loops", "for", "range", "if", "else", "elif", "debug", "debug_2", "timing", "lists", "dictionaries", "costs",
    "auto_unlock", "operators", "variables", "Items", "clear", "senses", "utilities", "can_harvest", "Entities",
    "get_world_size", "till", "use_item", "trade", "move", "multi_trade", "get_active_power", "North", "East",
    "South", "West", "functions", "import", "simulation", "get_water", "measure", "max_drones", "num_drones",
    "get_drone_id", "spawn_drone", "send", "receive", "underground_senses",
];

/// Every run of a leaderboard is repeated until the runs add up to this much game time, and the
/// score is their mean (MainSim.MIN_LEADERBOARD_TIME, two hours).
const LEADERBOARD_TOTAL_SECONDS: f64 = 7200.0;
/// A leaderboard run lasts until the script ends; one that has not ended by now is stopped.
const LEADERBOARD_MAX_RUN_SECONDS: f64 = 7200.0;
/// Real seconds one leaderboard run may take (it simulates far more than the usual minute).
const LEADERBOARD_WALL_LIMIT_SECONDS: f64 = 120.0;

fn leaderboard(name: &str) -> Option<&'static Lb> {
    let n = name.trim().to_lowercase();
    let n = n.strip_prefix("leaderboards.").unwrap_or(&n);
    LEADERBOARDS.iter().find(|l| l.name == n)
}

/// BuiltinFunctions.GetUnlockStrings(ResourceManager.GetAllUnlocks(), singleDrone): every unlock
/// at its top level, except that a single-drone board gets no megafarm and expand only to level 5
/// (an 8x8 farm). Fastest reset starts from the reset unlocks alone.
fn leaderboard_unlocks(lb: &Lb) -> Vec<String> {
    let mut list: Vec<String> = RESET_UNLOCKS.iter().map(|s| s.to_string()).collect();
    if lb.kind == LbKind::Reset {
        return list;
    }
    for u in UNLOCKS.iter() {
        if u.name == "explosive_drill" {
            continue;
        }
        if !lb.single_drone || u.name != "megafarm" {
            list.push(u.name.to_string());
        }
        if u.max_level > 1 {
            if lb.single_drone && u.name == "expand" {
                list.push("expand_5".into());
            } else if !lb.single_drone || u.name != "megafarm" {
                list.push(format!("{}_{}", u.name, u.max_level));
            }
        }
    }
    list
}

fn leaderboard_items(lb: &Lb) -> Items {
    let mut items = empty_items();
    for (name, n) in lb.start.iter() {
        items[item_id(name)] = *n;
    }
    items
}

/// The success condition MainSim.LeaderboardExecutionFinished checks once the program has ended.
fn leaderboard_success(sim: &Sim, lb: &Lb) -> bool {
    match lb.kind {
        LbKind::Reset => sim.num_unlocked(if lb.name == "fastest_reset" { "leaderboard" } else { "underground_leaderboard" }) > 0,
        LbKind::Farm => lb.goal.iter().all(|(name, n)| sim.items[item_id(name)] >= *n),
    }
}

/// A script that only calls leaderboard_run(Leaderboards.X, "file", speedup) names the board and
/// the file to run; returns them.
fn leaderboard_call(code: &str) -> Option<(&'static Lb, String)> {
    let at = code.find("leaderboard_run(")?;
    let args = &code[at + "leaderboard_run(".len()..];
    let args = &args[..args.find(')')?];
    let mut parts = args.split(',');
    let lb = leaderboard(parts.next()?)?;
    let file = parts.next()?.trim().trim_matches(|c| c == '"' || c == '\'').to_string();
    Some((lb, file))
}

struct Config {
    script: std::path::PathBuf,
    item: Option<String>,
    unlocks: Vec<String>,
    items: Items,
    world_size: Option<i32>,
    max_drones: Option<i32>,
    fps: f64,
    echo: Echo,
    leaderboard: Option<&'static Lb>,
}

struct RunResult {
    elapsed: f64,
    start_items: Items,
    end_items: Items,
    collected: Vec<(i64, Items)>,
    finished: bool,
    error: Option<String>,
    warnings: Vec<(String, u64)>,
    output: Vec<String>,
    stat_best: Items,
    world: (i32, i32),
    max_drones: i32,
    ticks_per_second: f64,
    /// leaderboard runs: whether the success condition held when the program ended
    lb_success: bool,
    /// leaderboard runs: game seconds at which the success condition first held
    goal_at: Option<f64>,
}

fn run_once(cfg: &Config, seed: i32) -> R<RunResult> {
    let name = cfg.script.file_stem().and_then(|s| s.to_str()).unwrap_or("main").to_string();
    let code = std::fs::read_to_string(&cfg.script).map_err(|e| format!("cannot read {}: {}", cfg.script.display(), e))?;
    let tree = parse_source(&name, &code)?;
    let sh = Rc::new(Shared {
        op_duration_ns: Cell::new(2500000),
        current_time: Cell::new(0),
        echo: cfg.echo,
        dir: cfg.script.parent().map(|p| p.to_path_buf()).unwrap_or_default(),
        output: RefCell::new(Vec::new()),
        warnings: RefCell::new(HashMap::new()),
        lb_nodes: Cell::new(cfg.leaderboard.map(|_| 0)),
        lb_modules: RefCell::new(HashSet::new()),
        trees: RefCell::new(Vec::new()),
    });
    let override_size = match cfg.world_size {
        Some(n) => (n, n),
        None => (0, 0),
    };
    let mut sim = Sim::new(sh.clone(), &cfg.unlocks, cfg.items.clone(), seed, override_size, cfg.max_drones);
    let start_items = sim.items.clone();
    let world = (sim.wx, sim.wy);
    let max_drones = sim.max_drones();
    let ticks_per_second = 1e9 / sim.op_duration as f64;
    // Execution's constructor registers the main file's code; too much of it stops the run.
    let code_check = register_leaderboard_code(&sh, &name, &tree);
    sh.trees.borrow_mut().push(tree.clone());
    sim.start_program_execution(tree);
    if let Err(e) = code_check {
        sim.error = Some(e);
    }
    let lb = cfg.leaderboard;
    let mut goal_at: Option<f64> = None;
    let item_id = cfg.item.as_deref().map(item_id);
    let (mut limit, max_limit, wall_limit) = match lb {
        Some(_) => (
            dur_from_seconds(LEADERBOARD_MAX_RUN_SECONDS),
            dur_from_seconds(LEADERBOARD_MAX_RUN_SECONDS),
            LEADERBOARD_WALL_LIMIT_SECONDS,
        ),
        None => (dur_from_seconds(RUN_SECONDS), dur_from_seconds(MAX_RUN_SECONDS), WALL_LIMIT_SECONDS),
    };
    // MainSim.Update: goalTime = sim.CurrentTime + min(deltaTime, 0.2) * TimeFactor, once per frame
    let frame = dur_from_seconds((1.0 / cfg.fps).min(0.2));
    let wall_start = std::time::Instant::now();
    loop {
        while sim.current_time < limit && sim.error.is_none() && !sim.finished {
            if wall_start.elapsed().as_secs_f64() > wall_limit {
                sim.error = Some(format!(
                    "something in this run is taking too long, make an optimization that keeps this run under {}s for whatever code you are running and push it (stopped after {:.1}s of real time at {:.1}s game time)",
                    wall_limit,
                    wall_start.elapsed().as_secs_f64(),
                    dur_seconds(sim.current_time)
                ));
                break;
            }
            let goal_time = (sim.current_time + frame).min(limit);
            while !sim.run_next_step(goal_time) {
                if sim.error.is_some() || sim.finished {
                    break;
                }
            }
            if let Some(lb) = lb {
                if goal_at.is_none() && leaderboard_success(&sim, lb) {
                    goal_at = Some(dur_seconds(sim.current_time));
                }
            }
        }
        if lb.is_some() {
            if !sim.finished && sim.error.is_none() {
                sim.error = Some(format!("the script had not ended after {:.0}s of game time; a leaderboard run only ends when every drone has returned", LEADERBOARD_MAX_RUN_SECONDS));
            }
            break;
        }
        let harvests = match item_id {
            Some(id) => sim.collected.iter().filter(|(_, b)| b[id] > 0.0).count(),
            None => MIN_HARVESTS,
        };
        if harvests >= MIN_HARVESTS || limit >= max_limit || sim.error.is_some() || sim.finished {
            break;
        }
        limit = (limit + dur_from_seconds(1.0)).min(max_limit);
    }
    let mut warnings: Vec<(String, u64)> = sh.warnings.borrow().iter().map(|(k, v)| (k.clone(), *v)).collect();
    warnings.sort();
    let output = std::mem::take(&mut *sh.output.borrow_mut());
    let lb_success = match lb {
        Some(lb) => sim.finished && sim.error.is_none() && leaderboard_success(&sim, lb),
        None => false,
    };
    Ok(RunResult {
        elapsed: dur_seconds(sim.current_time),
        start_items,
        end_items: sim.items.clone(),
        collected: std::mem::take(&mut sim.collected),
        finished: sim.finished,
        error: sim.error.clone(),
        warnings,
        output,
        stat_best: sim.stat_best.clone(),
        world,
        max_drones,
        ticks_per_second,
        lb_success,
        goal_at,
    })
}

fn group(n: f64) -> String {
    let neg = n < 0.0;
    let digits = format!("{:.0}", n.abs());
    let mut out = String::new();
    for (i, ch) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(ch);
    }
    if neg { format!("-{}", out) } else { out }
}

/// What one run harvested of the reported item.
struct Harvests {
    /// (seconds, amount) of every harvest that gave the item
    events: Vec<(f64, f64)>,
    /// the amount harvested after the first full-size harvest up to the last one, and the seconds
    /// between those two: the steady state, if there were two full-size harvests
    steady: Option<(f64, f64)>,
    /// harvests under half the biggest one (a stray cactus cut on its own, say)
    small: usize,
}

/// The steady state runs from full-size harvest to full-size harvest, where full-size is at least
/// half the biggest harvest of the run. Starting or ending the window on a small extra harvest
/// would cut a cycle short and misread the rate.
fn harvests(cfg: &Config, r: &RunResult) -> Option<Harvests> {
    let id = item_id(cfg.item.as_deref()?);
    let events: Vec<(f64, f64)> = r.collected.iter().filter(|(_, b)| b[id] > 0.0).map(|(t, b)| (dur_seconds(*t), b[id])).collect();
    let biggest = events.iter().map(|e| e.1).fold(0.0, f64::max);
    let full: Vec<usize> = (0..events.len()).filter(|i| events[*i].1 * 2.0 >= biggest).collect();
    let mut steady = None;
    if full.len() >= 2 {
        let (first, last) = (full[0], full[full.len() - 1]);
        let span = events[last].0 - events[first].0;
        if span > 0.0 {
            steady = Some((events[first + 1..=last].iter().map(|e| e.1).sum(), span));
        }
    }
    let small = events.len() - full.len();
    Some(Harvests { events, steady, small })
}

/// Prints one run's report and returns what its steady state is made of, if it harvested often
/// enough to have one: the amount harvested after the first full-size harvest and the seconds
/// that took.
fn report(cfg: &Config, seed: i32, r: &RunResult) -> Option<(f64, f64)> {
    let item = &cfg.item;
    let mut rate_out = None;
    let minutes = r.elapsed / 60.0;
    println!(
        "seed {}: simulated {:.1}s ({:.2} min), world {}x{}, max drones {}, {:.1} ticks/s{}",
        seed,
        r.elapsed,
        minutes,
        r.world.0,
        r.world.1,
        r.max_drones,
        r.ticks_per_second,
        if r.finished { " - the script ended on its own" } else { "" }
    );
    for line in r.output.iter() {
        println!("  {}", line);
    }
    for (id, name) in ITEM_NAMES.iter().enumerate() {
        let delta = r.end_items[id] - r.start_items[id];
        if delta != 0.0 && (item.is_none() || item.as_deref() == Some(name) || delta < 0.0) {
            println!("  {:16} {:>18}  ({:>14} /min)", name, group(delta), group(delta / minutes));
        }
    }
    if let Some(it) = item {
        let id = item_id(it);
        let h = harvests(cfg, r).unwrap();
        let events = &h.events;
        if events.len() >= 2 {
            let gaps: Vec<f64> = events.windows(2).map(|w| w[1].0 - w[0].0).collect();
            let mean_gap = gaps.iter().sum::<f64>() / gaps.len() as f64;
            let min_gap = gaps.iter().cloned().fold(f64::INFINITY, f64::min);
            let max_gap = gaps.iter().cloned().fold(0.0, f64::max);
            let mean_size = events.iter().map(|e| e.1).sum::<f64>() / events.len() as f64;
            let min_size = events.iter().map(|e| e.1).fold(f64::INFINITY, f64::min);
            println!(
                "  {}: {} harvests, {} per harvest (min {}), {:.2}s between harvests (min {:.2}, max {:.2}), first at {:.2}s",
                it,
                events.len(),
                group(mean_size),
                group(min_size),
                mean_gap,
                min_gap,
                max_gap,
                events[0].0
            );
            if let Some((total, span)) = h.steady {
                let rate = total / span * 60.0;
                if h.small == 0 {
                    println!("  steady state (first harvest to last): {} {}/min", group(rate), it);
                } else {
                    println!(
                        "  steady state (first full-size harvest to last, {} smaller harvest{} counted in): {} {}/min",
                        h.small,
                        if h.small == 1 { "" } else { "s" },
                        group(rate),
                        it
                    );
                }
                rate_out = Some((total, span));
            }
        } else if r.error.is_none() {
            println!("  {}: {} harvest(s) in {:.0}s, too few for a steady-state rate", it, events.len(), r.elapsed);
        }
        let best = r.stat_best[id];
        if best > 0.0 {
            println!("  in-game inventory tooltip would read: highest {} {}/min", group(best), it);
        }
    }
    for (w, n) in r.warnings.iter() {
        println!("  warning x{}: {}", n, w);
    }
    if let Some(e) = &r.error {
        println!("  ERROR: {}", e);
    }
    rate_out
}

/// Runs cfg once per seed on a pool of `workers` threads; results come back in seed order.
fn run_parallel(cfg: &Config, seeds: &[i32], workers: usize) -> Vec<R<RunResult>> {
    let next = std::sync::atomic::AtomicUsize::new(0);
    let results: Vec<std::sync::Mutex<Option<R<RunResult>>>> = seeds.iter().map(|_| std::sync::Mutex::new(None)).collect();
    std::thread::scope(|scope| {
        for _ in 0..workers.min(seeds.len()).max(1) {
            let spawned = std::thread::Builder::new().stack_size(256 << 20).spawn_scoped(scope, || loop {
                let job = next.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                if job >= seeds.len() {
                    break;
                }
                let r = run_once(cfg, seeds[job]);
                *results[job].lock().unwrap() = Some(r);
            });
            if let Err(e) = spawned {
                eprintln!("error: cannot start a worker thread: {}", e);
                std::process::exit(1);
            }
        }
    });
    results.into_iter().map(|m| m.into_inner().unwrap().unwrap_or_else(|| Err("the run did not finish".into()))).collect()
}

/// Runs cfg with seeds first_seed, first_seed + 1, ... on `workers` threads, each taking the next
/// run as soon as it finishes one (at most `limit` runs). `accept` sees the results in seed order
/// and returns false once it needs no more; runs already under way past that point are dropped.
fn run_stream(cfg: &Config, first_seed: i32, workers: usize, limit: Option<usize>, mut accept: impl FnMut(i32, R<RunResult>) -> bool) {
    use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
    let next = AtomicUsize::new(0);
    let stop = AtomicBool::new(false);
    let (tx, rx) = std::sync::mpsc::channel::<(usize, R<RunResult>)>();
    std::thread::scope(|scope| {
        for _ in 0..workers.max(1).min(limit.unwrap_or(usize::MAX).max(1)) {
            let tx = tx.clone();
            let (next, stop) = (&next, &stop);
            let spawned = std::thread::Builder::new().stack_size(256 << 20).spawn_scoped(scope, move || loop {
                if stop.load(Ordering::Relaxed) {
                    break;
                }
                let job = next.fetch_add(1, Ordering::Relaxed);
                if limit.map_or(false, |l| job >= l) {
                    break;
                }
                let r = run_once(cfg, first_seed.wrapping_add(job as i32));
                if tx.send((job, r)).is_err() {
                    break;
                }
            });
            if let Err(e) = spawned {
                eprintln!("error: cannot start a worker thread: {}", e);
                std::process::exit(1);
            }
        }
        drop(tx);
        let mut pending: std::collections::BTreeMap<usize, R<RunResult>> = std::collections::BTreeMap::new();
        let mut want = 0usize;
        let mut accepting = true;
        for (job, r) in rx.iter() {
            if !accepting {
                continue;
            }
            pending.insert(job, r);
            while let Some(r) = pending.remove(&want) {
                if !accept(first_seed.wrapping_add(want as i32), r) {
                    accepting = false;
                    stop.store(true, Ordering::Relaxed);
                    break;
                }
                want += 1;
            }
        }
    });
}

fn clock(seconds: f64) -> String {
    let ms = (seconds * 1000.0) as i64;
    let (h, m, s, ms) = (ms / 3_600_000, ms / 60_000 % 60, ms / 1000 % 60, ms % 1000);
    if h > 0 { format!("{}:{:02}:{:02}.{:03}", h, m, s, ms) } else { format!("{}:{:02}.{:03}", m, s, ms) }
}

/// MainSim.LeaderboardExecutionFinished: each run lasts until the script ends; the runs repeat
/// (with fresh seeds) until they add up to two hours of game time, and the score is their mean time,
/// uploaded in whole milliseconds. A run that ends without meeting the goal ends the attempt with
/// no score. Returns false if any script failed.
fn run_leaderboards(cfgs: &[Config], first_seed: i32, fixed_runs: Option<i32>, workers: usize, brief: bool) -> bool {
    let mut all_ok = true;
    let mut rows: Vec<(f64, String)> = Vec::new();
    for (ci, cfg) in cfgs.iter().enumerate() {
        let lb = cfg.leaderboard.unwrap();
        if !brief && cfgs.len() > 1 {
            println!("{}== {} ==", if ci > 0 { "\n" } else { "" }, cfg.script.display());
        }
        let mut runs: Vec<(i32, RunResult)> = Vec::new();
        let mut total = 0.0;
        let mut failure: Option<String> = None;
        let limit = fixed_runs.map(|n| n.max(1) as usize);
        run_stream(cfg, first_seed, workers, limit, |seed, r| {
            let r = match r {
                Ok(r) => r,
                Err(e) => {
                    failure = Some(format!("run {} (seed {}): {}", runs.len() + 1, seed, e));
                    return false;
                }
            };
            total += r.elapsed;
            let ok = r.lb_success;
            runs.push((seed, r));
            if !ok {
                let (seed, r) = runs.last().unwrap();
                let why = match &r.error {
                    Some(e) => e.clone(),
                    None => format!(
                        "the script ended at {:.3}s without meeting the goal ({})",
                        r.elapsed,
                        lb.goal.iter().map(|(n, g)| format!("{} {} of {}", n, group(r.end_items[item_id(n)]), group(*g))).collect::<Vec<_>>().join(", ")
                    ),
                };
                failure = Some(format!("run {} (seed {}): {}", runs.len(), seed, why));
                return false;
            }
            !(fixed_runs.is_none() && total >= LEADERBOARD_TOTAL_SECONDS)
        });
        let n = runs.iter().filter(|(_, r)| r.lb_success).count();
        let times: Vec<f64> = runs.iter().filter(|(_, r)| r.lb_success).map(|(_, r)| r.elapsed).collect();
        let mean = if n > 0 { times.iter().sum::<f64>() / n as f64 } else { 0.0 };
        let score = (mean * 1000.0).floor() / 1000.0;
        let min = times.iter().cloned().fold(f64::INFINITY, f64::min);
        let max = times.iter().cloned().fold(0.0, f64::max);
        let lag: Vec<f64> = runs.iter().filter_map(|(_, r)| r.goal_at.map(|g| r.elapsed - g)).collect();
        let mean_lag = if lag.is_empty() { 0.0 } else { lag.iter().sum::<f64>() / lag.len() as f64 };
        if !brief {
            // The first run in full, and the failed one if it is another.
            if let Some((seed, r)) = runs.first() {
                report(cfg, *seed, r);
            }
            if failure.is_some() && runs.len() > 1 {
                let (seed, r) = runs.last().unwrap();
                println!();
                report(cfg, *seed, r);
            }
            println!();
            println!("Leaderboards.{} with {}", lb.name, cfg.script.display());
            if n > 1 {
                let list: Vec<String> = times.iter().map(|t| format!("{:.3}", t)).collect();
                if list.len() <= 20 {
                    println!("  run times: {}", list.join(" "));
                }
            }
        }
        let line = match &failure {
            Some(f) => {
                all_ok = false;
                format!("FAILED, no score: {}", f)
            }
            None => {
                let covered = if fixed_runs.is_none() {
                    format!("{} simulated", clock(total))
                } else {
                    format!("{} simulated, short of the game's {}h", clock(total), LEADERBOARD_TOTAL_SECONDS / 3600.0)
                };
                format!(
                    "score {} ({:.3}s) = mean of {} run{} ({}); min {:.3}s, max {:.3}s; goal met {:.3}s before the end on average",
                    clock(score),
                    score,
                    n,
                    if n == 1 { "" } else { "s" },
                    covered,
                    min,
                    max,
                    mean_lag
                )
            }
        };
        if brief {
            let key = if failure.is_some() { f64::INFINITY } else { score };
            rows.push((key, format!("{:<18} {}  {}", lb.name, line, cfg.script.display())));
        } else {
            println!("  {}", line);
        }
    }
    if brief {
        rows.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));
        for (_, line) in rows.iter() {
            println!("{}", line);
        }
    }
    all_ok
}

const USAGE: &str = "usage: tfwr_sim <script.py>... [--seed N] [--seeds N] [--jobs N] [--item NAME]
                [--save save.json] [--size N] [--drones N] [--set unlock=level] [--give item=n]
                [--fps N] [--quiet] [--brief] [--leaderboard NAME]

Runs each script on a fresh farm with the unlocks and items from save.json and reports what it
produced. Every run simulates one game minute, or longer (up to ten) if the script needs it to
harvest the reported item three times. Several scripts and --seeds run in parallel, --jobs at a
time (default: one per CPU core), and every script sees the same seeds.
--brief prints one line per script, best first, instead of the per-run reports.
--size / --drones override the world size and drone limit that the save's expand and megafarm
levels give (16x16 and 32 for expand_7 and megafarm_5).

--leaderboard NAME (cactus, maze, hay_single, fastest_reset, ...) runs the script the way
leaderboard_run() does: the board's fixed unlocks and items instead of save.json's, each run lasting
until the script ends, repeated until the runs cover two hours of game time, and scored by their
mean time. A script that calls leaderboard_run(Leaderboards.X, \"file\", speedup) is run that way
without the option. --seeds N runs exactly N times instead of covering two hours.";

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut scripts: Vec<String> = Vec::new();
    let mut seed: Option<i32> = None;
    let mut seeds = 1;
    let mut seeds_given = false;
    let mut lb_opt: Option<&'static Lb> = None;
    let mut jobs: Option<usize> = None;
    let mut item: Option<String> = None;
    let mut save: Option<String> = None;
    let mut size: Option<i32> = None;
    let mut drones: Option<i32> = None;
    let mut sets: Vec<(String, i32)> = Vec::new();
    let mut gives: Vec<(String, f64)> = Vec::new();
    let mut fps = 60.0;
    let mut quiet = false;
    let mut brief = false;
    let mut i = 0;
    let fail = |msg: &str| -> ! {
        eprintln!("{}\n\n{}", msg, USAGE);
        std::process::exit(2);
    };
    while i < args.len() {
        let a = args[i].as_str();
        let mut val = || -> String {
            i += 1;
            match args.get(i) {
                Some(v) => v.clone(),
                None => fail(&format!("{} needs a value", a)),
            }
        };
        match a {
            "--seed" => seed = Some(val().parse().unwrap_or_else(|_| fail("--seed needs an integer"))),
            "--seeds" => {
                seeds = val().parse().unwrap_or_else(|_| fail("--seeds needs an integer"));
                seeds_given = true;
            }
            "--leaderboard" => {
                let v = val();
                lb_opt = Some(leaderboard(&v).unwrap_or_else(|| {
                    fail(&format!("unknown leaderboard {}; one of: {}", v, LEADERBOARDS.iter().map(|l| l.name).collect::<Vec<_>>().join(", ")))
                }));
            }
            "--jobs" => jobs = Some(val().parse().unwrap_or_else(|_| fail("--jobs needs an integer"))),
            "--item" => item = Some(val()),
            "--save" => save = Some(val()),
            "--size" => size = Some(val().parse().unwrap_or_else(|_| fail("--size needs an integer"))),
            "--drones" => drones = Some(val().parse().unwrap_or_else(|_| fail("--drones needs an integer"))),
            "--fps" => fps = val().parse().unwrap_or_else(|_| fail("--fps needs a number")),
            "--set" | "--give" => {
                let v = val();
                let (k, n) = match v.split_once('=') {
                    Some(p) => p,
                    None => fail(&format!("{} needs name=value", a)),
                };
                let n: f64 = n.parse().unwrap_or_else(|_| fail(&format!("{} needs name=number", a)));
                if a == "--set" {
                    sets.push((k.to_string(), n as i32));
                } else {
                    gives.push((k.to_string(), n));
                }
            }
            "--quiet" => quiet = true,
            "--brief" => {
                brief = true;
                quiet = true;
            }
            "-h" | "--help" => {
                println!("{}", USAGE);
                return;
            }
            "--minutes" => fail("--minutes is gone: every run now simulates one game minute (see below)"),
            _ if a.starts_with("--") => fail(&format!("unknown option {}", a)),
            _ => scripts.push(a.to_string()),
        }
        i += 1;
    }
    if scripts.is_empty() {
        fail("no script given");
    }
    let scripts: Vec<std::path::PathBuf> = scripts
        .iter()
        .map(|s| {
            let p = std::path::PathBuf::from(s);
            if p.exists() { p } else { std::path::PathBuf::from(".").join(&p) }
        })
        .collect();
    let dir = scripts[0].parent().map(|p| p.to_path_buf()).unwrap_or_default();
    let save_path = match save {
        Some(s) => std::path::PathBuf::from(s),
        None => dir.join("save.json"),
    };

    let mut unlocks: Vec<String> = Vec::new();
    let mut items = empty_items();
    match std::fs::read_to_string(&save_path) {
        Ok(text) => match parse_json(&text) {
            Ok(json) => {
                for u in json.get("unlocks").map(|u| u.arr()).unwrap_or(&[]) {
                    if let Json::Str(s) = u {
                        unlocks.push(s.clone());
                    }
                }
                let list = json.get("items").and_then(|i| i.get("serializeList")).map(|l| l.arr()).unwrap_or(&[]);
                for e in list {
                    if let (Some(Json::Str(n)), Some(Json::Num(nr))) = (e.get("name"), e.get("nr")) {
                        if let Some(id) = ITEM_NAMES.iter().position(|x| x == n) {
                            items[id] = *nr;
                        }
                    }
                }
            }
            Err(e) => fail(&format!("cannot parse {}: {}", save_path.display(), e)),
        },
        Err(_) => eprintln!("note: {} not found, starting with nothing unlocked", save_path.display()),
    }
    let apply_overrides = |unlocks: &mut Vec<String>, items: &mut Items| {
        for (k, level) in sets.iter() {
            unlocks.retain(|u| u != k && !(u.starts_with(&format!("{}_", k)) && u[k.len() + 1..].parse::<i32>().is_ok()));
            unlocks.push(if *level > 1 { format!("{}_{}", k, level) } else { k.clone() });
        }
        for (k, n) in gives.iter() {
            match ITEM_NAMES.iter().position(|x| x == k) {
                Some(id) => items[id] = *n,
                None => fail(&format!("unknown item {}", k)),
            }
        }
    };
    apply_overrides(&mut unlocks, &mut items);
    if let Some(it) = &item {
        if !ITEM_NAMES.contains(&it.as_str()) {
            fail(&format!("unknown item {}", it));
        }
    }
    let seeds: i32 = seeds.max(1);
    let total_jobs = scripts.len() * seeds as usize;
    let echo = if quiet {
        Echo::Off
    } else if total_jobs == 1 {
        Echo::Live
    } else {
        Echo::Buffered
    };
    // --item applies to every script; otherwise each script's item is guessed from its file name,
    // and a script whose name says nothing (cactus_v2.py) reports the same item as the first one.
    let mut guessed: Option<String> = None;
    let cfgs: Vec<Config> = scripts
        .into_iter()
        .map(|script| {
            // A leaderboard run: from --leaderboard, or from a launcher script's leaderboard_run().
            let (script, lb) = match lb_opt {
                Some(lb) => (script, Some(lb)),
                None => match std::fs::read_to_string(&script).ok().as_deref().and_then(leaderboard_call) {
                    Some((lb, file)) => (script.parent().map(|p| p.to_path_buf()).unwrap_or_default().join(format!("{}.py", file)), Some(lb)),
                    None => (script, None),
                },
            };
            if let Some(lb) = lb {
                if lb.dlc {
                    fail(&format!("Leaderboards.{} needs the mining DLC, which this simulator does not port", lb.name));
                }
                let mut unlocks = leaderboard_unlocks(lb);
                let mut items = leaderboard_items(lb);
                apply_overrides(&mut unlocks, &mut items);
                let item = item.clone().or_else(|| lb.goal.first().map(|g| g.0.to_string()));
                let echo = if quiet { Echo::Off } else { Echo::Buffered };
                return Config { script, item, unlocks, items, world_size: size, max_drones: drones, fps, echo, leaderboard: Some(lb) };
            }
            let stem = script.file_stem().and_then(|s| s.to_str()).unwrap_or("").to_string();
            let by_name = item_from_stem(&stem);
            if guessed.is_none() {
                guessed = by_name.clone();
            }
            let item = item.clone().or(by_name).or_else(|| guessed.clone());
            Config { script, item, unlocks: unlocks.clone(), items: items.clone(), world_size: size, max_drones: drones, fps, echo, leaderboard: None }
        })
        .collect();

    let first_seed = seed.unwrap_or_else(|| {
        (std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_nanos()).unwrap_or(1) % 1_000_000_007) as i32
    });

    let cores = std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1);
    if cfgs.iter().any(|c| c.leaderboard.is_some()) {
        if cfgs.iter().any(|c| c.leaderboard.is_none()) {
            fail("leaderboard runs and ordinary runs cannot be mixed in one command");
        }
        let fixed_runs = if seeds_given { Some(seeds) } else { None };
        let ok = run_leaderboards(&cfgs, first_seed, fixed_runs, jobs.unwrap_or(cores).max(1), brief);
        if !ok {
            std::process::exit(1);
        }
        return;
    }

    // One job per (script, seed). Each simulation is single-threaded and shares nothing, so the
    // jobs run on a pool of worker threads and are reported in order once all have finished.
    let workers = jobs.unwrap_or(cores).max(1).min(total_jobs);
    let next = std::sync::atomic::AtomicUsize::new(0);
    let results: Vec<std::sync::Mutex<Option<R<RunResult>>>> = (0..total_jobs).map(|_| std::sync::Mutex::new(None)).collect();
    std::thread::scope(|scope| {
        for _ in 0..workers {
            // The interpreter recurses with the script's call depth, so give it a deep stack.
            let spawned = std::thread::Builder::new().stack_size(256 << 20).spawn_scoped(scope, || loop {
                let job = next.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                if job >= total_jobs {
                    break;
                }
                let cfg = &cfgs[job / seeds as usize];
                let seed = first_seed.wrapping_add((job % seeds as usize) as i32);
                let r = run_once(cfg, seed);
                *results[job].lock().unwrap() = Some(r);
            });
            if let Err(e) = spawned {
                eprintln!("error: cannot start a worker thread: {}", e);
                std::process::exit(1);
            }
        }
    });

    let mut failed = false;
    let mut summary: Vec<String> = Vec::new();
    if brief {
        // One line per script, best first, for comparing many variants at a glance.
        let mut rows: Vec<(f64, String)> = Vec::new();
        for (ci, cfg) in cfgs.iter().enumerate() {
            let (mut total, mut span, mut count, mut amount, mut gap_sum, mut gaps) = (0.0, 0.0, 0usize, 0.0, 0.0, 0usize);
            let (mut least, mut errors, mut warnings, mut runs) = (f64::INFINITY, 0usize, 0u64, 0usize);
            let mut first_error = String::new();
            for s in 0..seeds as usize {
                let r = match results[ci * seeds as usize + s].lock().unwrap().take() {
                    Some(Ok(r)) => r,
                    Some(Err(e)) => {
                        errors += 1;
                        if first_error.is_empty() {
                            first_error = e;
                        }
                        continue;
                    }
                    None => continue,
                };
                runs += 1;
                if let Some(e) = &r.error {
                    errors += 1;
                    if first_error.is_empty() {
                        first_error = e.clone();
                    }
                }
                warnings += r.warnings.iter().map(|w| w.1).sum::<u64>();
                if let Some(h) = harvests(cfg, &r) {
                    if let Some((t, sp)) = h.steady {
                        total += t;
                        span += sp;
                    }
                    let biggest = h.events.iter().map(|e| e.1).fold(0.0, f64::max);
                    let full: Vec<&(f64, f64)> = h.events.iter().filter(|e| e.1 * 2.0 >= biggest).collect();
                    count += full.len();
                    amount += full.iter().map(|e| e.1).sum::<f64>();
                    least = full.iter().map(|e| e.1).fold(least, f64::min);
                    gap_sum += full.windows(2).map(|w| w[1].0 - w[0].0).sum::<f64>();
                    gaps += full.len().saturating_sub(1);
                }
            }
            if errors > 0 {
                failed = true;
            }
            let rate = if span > 0.0 { total / span * 60.0 } else { 0.0 };
            let mut line = format!(
                "{:>14} {}/min  {:>7.2}s cycle  {:>12} per harvest (min {:>12})  {}",
                group(rate),
                cfg.item.as_deref().unwrap_or("?"),
                if gaps > 0 { gap_sum / gaps as f64 } else { 0.0 },
                group(if count > 0 { amount / count as f64 } else { 0.0 }),
                group(if count > 0 { least } else { 0.0 }),
                cfg.script.display()
            );
            if warnings > 0 {
                line.push_str(&format!("  [{} warnings]", warnings));
            }
            if errors > 0 {
                line.push_str(&format!("  [ERROR in {} of {} runs: {}]", errors, runs.max(errors), first_error));
            }
            rows.push((rate, line));
        }
        rows.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));
        println!(
            "{} seed{} each, from seed {}; cycle and per-harvest figures leave out harvests under half the biggest",
            seeds,
            if seeds == 1 { "" } else { "s" },
            first_seed
        );
        for (_, line) in rows.iter() {
            println!("{}", line);
        }
        if failed {
            std::process::exit(1);
        }
        return;
    }
    for (ci, cfg) in cfgs.iter().enumerate() {
        if cfgs.len() > 1 {
            println!("{}== {} ==", if ci > 0 { "\n" } else { "" }, cfg.script.display());
        }
        let mut rates: Vec<f64> = Vec::new();
        let (mut all_total, mut all_span) = (0.0, 0.0);
        for s in 0..seeds as usize {
            let seed = first_seed.wrapping_add(s as i32);
            let r = match results[ci * seeds as usize + s].lock().unwrap().take() {
                Some(Ok(r)) => r,
                Some(Err(e)) => {
                    eprintln!("error: {}", e);
                    failed = true;
                    break;
                }
                None => {
                    eprintln!("error: the run for seed {} did not finish", seed);
                    failed = true;
                    break;
                }
            };
            if let Some((total, span)) = report(cfg, seed, &r) {
                rates.push(total / span * 60.0);
                all_total += total;
                all_span += span;
            }
            if r.error.is_some() {
                failed = true;
            }
        }
        if !rates.is_empty() && (seeds > 1 || cfgs.len() > 1) {
            // Pooled over the seeds (all harvests over all the time they took), not the mean of the
            // per-seed rates: with only a few harvests per run that mean reads a percent or two high.
            let mean = all_total / all_span * 60.0;
            let min = rates.iter().cloned().fold(f64::INFINITY, f64::min);
            let max = rates.iter().cloned().fold(0.0, f64::max);
            let label = if cfgs.len() > 1 {
                format!("{} {}", cfg.script.display(), cfg.item.as_deref().unwrap_or(""))
            } else {
                cfg.item.as_deref().unwrap_or("").to_string()
            };
            summary.push(format!(
                "{}: mean {} /min over {} seed{} (min {}, max {})",
                label,
                group(mean),
                rates.len(),
                if rates.len() == 1 { "" } else { "s" },
                group(min),
                group(max)
            ));
        }
    }
    if !summary.is_empty() {
        println!();
        for line in summary.iter() {
            println!("{}", line);
        }
    }
    if failed {
        std::process::exit(1);
    }
}
