#!/bin/bash
v4l2-ctl \
--set-ctrl=white_balance_auto_preset=6 \
--set-ctrl=exposure_dynamic_framerate=1 \
--set-ctrl=brightness=70 \
--set-ctrl=contrast=50 \
--set-ctrl=exposure_metering_mode=2 \
--set-ctrl=auto_exposure=1
