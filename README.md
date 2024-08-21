# HealthChat

The recommended version of python is 3.8 to avoid gradio error messages.

```bash
git clone https://github.com/yupu891101/HealthChat.git
cd HealthChat
bash install.bash
```
這裡不用 pip install -r requirements.txt 改用 bash 因為有依賴項的問題。

### Finetuned Taiwan-LLM-13B

```bash
cd taiwan_llama/
git Ifs install
git clone https://huggingface.co/huangyt/module_v7
```

### Run
```bash
python launch.py
```
 create --name test python=3.8