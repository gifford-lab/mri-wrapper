docker run -it --rm --device /dev/nvidiactl \
	--device /dev/nvidia-uvm \
	--device /dev/nvidia0 \
	--device /dev/nvidia1 \
	--device /dev/nvidia2 \
	-v /cluster/zeng/code/research/mri-wrapper/input:/model \
	-v /cluster/zeng/research/dl_testbench/NFKB_peakPred_401bp:/data \
	haoyangz/mri-wrapper python main.py /model/runparam.list 2
