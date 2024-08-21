# HealthChat

This project has been tested with Python version 3.10.

## Installation

1. **Clone the Repository:**

    Instead of using `pip install -r requirements.txt`, we use a bash script due to dependency issues.

    ```bash
    git clone https://github.com/yupu891101/HealthChat.git
    cd HealthChat
    bash install.bash
    ```
2. **Clone the Ollama Repository:**

    Clone the Ollama repository to obtain the necessary code and resources:

    ```bash
    git clone https://github.com/ollama/ollama.git
    ```

3. **Download the Fine-tuned Taiwan-LLM-13B Model:**

    ```bash
    cd taiwan_llama
    git lfs install
    git clone https://huggingface.co/huangyt/module_v7
    ```

4. **Install DDSP-SVC for Voice Synthesis:**
    
    Clone the [DDSP-SVC](https://github.com/yxlllc/DDSP-SVC) repository and install its dependencies:

    ```bash
    cd ../
    git clone https://github.com/yxlllc/DDSP-SVC.git
    cd DDSP-SVC
    pip install pip==24.0  # Ensure pip is downgraded to avoid compatibility issues
    pip install -r requirements.txt
    ```
    :::info Note: Some packages listed in requirements.txt require pip version <24.1. Therefore, it's necessary to first downgrade pip to version 24.0 before installing the dependencies.

5. **Download and Set Up Additional Models:**

   - **Model 0:** Download the [model_0.pt](https://github.com/yxlllc/DDSP-SVC/releases/download/5.0/model_0.pt) file and place it into the `exp` folder within the DDSP-SVC directory.
   - **RMVPE Extractor:** Download the pre-trained [RMVPE](https://github.com/yxlllc/RMVPE/releases/download/230917/rmvpe.zip) extractor, unzip it, and place the contents into the `pretrain/rmvpe` folder within the DDSP-SVC directory.
   - **NSF-HiFiGAN Vocoder:** Download the pre-trained [NSF-HiFiGAN](https://github.com/openvpi/vocoders/releases/download/nsf-hifigan-44.1k-hop512-128bin-2024.02/nsf_hifigan_44.1k_hop512_128bin_2024.02.zip) vocoder, unzip it, and place the contents into the `pretrain/nsf_hifigan/model` folder within the DDSP-SVC directory.
   - **ContentVec Encoder:** Download the pre-trained [ContentVec](https://ibm.ent.box.com/s/z1wgl1stco8ffooyatzdwsqn2psd9lrr) encoder and place it into the `pretrain/contentvec` folder within the DDSP-SVC directory.

6. **Modify Configuration Files:**

   Update the `diffusion-fast.yaml` configuration file in the `DDSP-SVC/configs` directory. Specifically, you need to modify the `ckpt` path for the vocoder to point to `pretrain/nsf_hifigan/model/model.ckpt`.

### Directory Structure

The directory structure of the `DDSP-SVC` folder should look like this:

```markdown
DDSP-SVC/   
├── configs/    
│   ├── diffusion-fast.yaml 
│   └── ... 
├── exp/    
│   └── model_0.pt  
├── pretrain/   
│   ├── rmvpe/  
│   │   └── model.pt    
│   ├── nsf_hifigan/    
│   │   └── model/
│   │       ├── config.json 
│   │       ├── model.ckpt  
│   │       ├── NOTICE.txt  
│   │       └── NOTICE.zh-CN.txt    
│   └── contentvec/ 
│       └── checkpoint_best_legacy_500.pt   
└── scripts/    
    ├── preprocess.py   
    └── train_diff.py   
```

## Running the Project

To run the project, simply execute the following command in the terminal:

```bash
python launch.py
```
