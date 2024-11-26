# Installing Batfish

## Batfish Service (via Docker)

```shell
$ docker pull batfish/allinone
$ docker run --name batfish -d -p 8888:8888 -p 9997:9997 -p 9996:9996 batfish/allinone
```

## Batfish Client (pybatfish)

```shell
# Create Python environment
$ python3 -m venv venv
$ source venv/bin/activate

# Install pybatfish
$ pip3 install pybatfish
```