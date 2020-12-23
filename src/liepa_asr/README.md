Precondition: see README.md in parent folder.

Create toolchain

```
qitoolchain create atom286 $HOME/bin/ctc-linux64-atom-2.8.6.23-20191127_161825/toolchain.xml
```


Setup config:

```
qibuild add-config atom286 --toolchain atom286  --default
```

Build Pocketsphinx dependencies:
```
(cd sphinxbase && PYTHON=python3 ./autogen.sh)
(cd pocketsphinx && PYTHON=python3 ./autogen.sh)
```

Prepare build dir:
```
qibuild configure -c atom286
```

Build recogintion module
```
qibuild make -c atom286 -j 5
```

Copy recogintion module to robot(where 192.168.1.8 is robot ip):
```
scp build-atom286/sdk/bin/LiepaASR nao@192.168.1.8:/home/nao/naoqi/lib
```

Register LiepaASR service in `/home/nao/naoqi/preferences/autoload.ini`.


