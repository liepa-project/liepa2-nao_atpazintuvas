Based on https://qiita.com/tkawata1025/items/afbda4b9a491dfac56d4

```
sudo apt install cmake
pip install qibuild --user
echo 'PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
```

Create conda env

```
conda create --name l2nao
```

Activate conda env 

```
conda activate l2nao
```

Pull sphinx source:
```
git submodule update --init --recursive
```
