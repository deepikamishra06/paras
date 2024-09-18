#!/bin/bash
while true; do
   rclone copy parassocteamup:paras/input_database/func_enable.xlsx /home/raspi4/paras/input_database/
   rclone copy parassocteamup:paras/input_database/user_input_mails_rx.xlsx /home/raspi4/paras/input_database/
   rclone move parassocteamup:paras/input_database/Hotel_and_Restaurants /home/raspi4/paras/input_database/
   rclone copy /home/raspi4/paras/output_database/attendance.csv parassocteamup:paras/output_database/
   rclone copy /home/raspi4/paras/output_database/detailed_entry_sheets_daily parassocteamup:paras/output_database/detailed_entry_sheets_daily
   rclone copy /home/raspi4/paras/output_database/Final_In_Out_daily parassocteamup:paras/output_database/Final_In_Out_daily
   rclone move /home/raspi4/paras/output_database/output_images parassocteamup:paras/output_database/output_images
   chmod 777 -R /home/raspi4/
   sleep 120 
done
