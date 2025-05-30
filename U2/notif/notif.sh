#--image-path "/storage/emulated/0/DCIM/Facebook/FB_IMG_1744677621250.jpg"
termux-notification --title "U2 Device" \
	--button1 "Exit" \
	--button1-action "echo -1 > ~/pipes/pipe" \
	--id 21 \
	--priority "high" \
	--ongoing \
