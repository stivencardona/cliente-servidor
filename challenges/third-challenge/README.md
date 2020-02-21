## Build commands:

Before of execute run:

```bash
mkdir storage-server
mkdir storage-client
cd storage-server
head -c 1G /dev/urandom > testdata
cd stirage-client
head -c 1G /dev/urandom > testdata
```

## Execute

In diferents consoles execute

```python
python3 server.py
python3 client.py
```

For the client with `download` input start download testdata of the storage-server folder and `upload` input start upload of the testdata in storage-client
