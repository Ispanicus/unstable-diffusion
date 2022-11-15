git clone https://github.com/CompVis/stable-diffusion.git ../stable-diffusion

conda env create -f ../stable-diffusion/environment.yaml
conda activate ldm

python -m pip install pip -U
python -m pip install -e .

:: %SystemRoot%\System32\cmd.exe /K "C:\Users\Christoffer\miniconda3\condabin\conda.bat activate ldm"