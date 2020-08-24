Modem_NotFound = 0o0001
Extra = 0o0002
SendEmail= 0o0006
PauseRecording = 7
ResumeRecording = 8
Processed_Call_End_Success = 9
Processed_Call_End_Fail= 10
Split_Log = 11
TcpdumpStartRecording= 12
TcpdumpStopRecording= 13

DebugLog= 35
AndroidLogStart= 36
AndroidLogStop= 37
StartStatement= 38
EndStatement= 39
SetTagName= 40
SetEnableGPS= 41
Message= 42
SetBTTagName= 43
Note_Added= 101
use_external_gps= 102
NonDBInsertDebugLog= 100
AddGPSCancel= 104

Android_Internal_Handover_Attempt= 1000
Android_Internal_Handover_Complete= 1001
Android_Internal_Handover_Failure= 1002
PDP_Act_Duration = 1003
Attach_Duration = 1004
Attach = 1005
RoutingAreaUpdate = 1006
ActivatePDPContext = 1007
LocationAreaUpdate = 1008
Authentication = 1009
CM_SERVICE = 1010
MM_ABORT = 1011
MM_STATUS = 1012
Android_Internal_Modem_Conf_Write_Resp= 1013
Android_Internal_Modem_Offline_Resp= 1014
Android_Internal_Modem_Conf_Read_Resp_Len= 1015
Android_Internal_Modem_Conf_Read_Resp_Data= 1016
Android_Internal_Modem_Rm_Resp= 1017
Android_Internal_Modem_Reset_Resp= 1018
GSM_DSF= 1019
RoutingAreaUpdateSuccess = 1022
RoutingAreaUpdateFail = 1023
RrcConnectionEstablished = 1024
RrcConnectionReject = 1025
PDP_DeAct_Duration = 1026
Restroing_LTE_PCI_Lock= 1027
Restore_LTE_PCI_Lock_Complete= 1028
E911_Test= 1029
ESMInformationResponse= 1030
PDNConnectivityRequest= 1031


Handover_Complete = 10013
Handover_Fail = 10014
Android_Dial = 10015
Handover_Command_3G = 10016
Handover_Completed_3G = 10017
Handover_Fail_3G = 10018

Handover_Command = 10033

SMS_Received = 10034

MMS_WAP_PUSH_RECEIVED = 20609
MMS_DOWNLOAD_DONE = 20610

InterRAT_Handover_2G_To_3G= 10046
InterRAT_Handover_3G_To_2G= 10047

Remote_Match_Success= 10050
Remote_Match_Fail= 10051
Force_NetworkMode_GSM= 10052
Force_NetworkMode_WCDMA= 10053
Force_NetworkMode_WCDMA_GSM= 10054
Force_NetworkMode_LTE= 10055
Force_NetworkMode_LTE_WCDMA= 10056
Force_NetworkMode_LTE_WCDMA_GSM= 10057
InterRAT_Handover_From_3G_Failure= 10058
Call_SRVCC_To_WCDMA = 10059
DriveTest_Recovery_From_Reboot = 10071
SRVCC= 10072

Diag_Recording_Reset= 10100
No_Service_Recovery= 10101
MM_Substate_Stuck_Prevention= 10102
WCDMA_RADIO_LINK_FAILURE= 10105
GSM_RADIO_LINK_FAILURE= 10106
LTE_RRC_RADIO_LINK_FAILURE= 10107

Voice_WCDMA_TO_GSM_HO_COMPLETE= 10108
Ping_No_Buffer_Space_Available= 10109
InLogTag= 10501

RAT_Lock= 10502
LTE_PCI_Lock= 10503
LTE_EARFCN_Lock= 10504
WCDMA_DedMode_PSC_Stay= 10505
WCDMA_UARFCN_Lock= 10506
GSM_WCDMA_Band_Lock= 10507
LTE_Band_Lock= 10508
R99_Lock= 10509
GPRS_Lock= 10510
Ignore_Cell_Barred= 10511

Set_APN = 20631
Force_Lock_Done= 10532

TakePhoto= 10533
CrossSector_Detected= 10534
Start_QMDL= 10535
Stop_QMDL= 10536
ScreenshotSector= 10537
CrossSector_Detected_Unset= 10538
auto_screenshot_start= 10539
auto_screenshot_end= 10540
auto_screenshot_on_error= 10543
add_photo= 10544

IMS_REG_ATTEMPT= 10541
IMS_REG_SUCCESS= 10542


Data_Modem_Connecting = 20001
Data_Modem_Connected = 20002
Data_Modem_Disconnecting = 20003
Data_Modem_Disconnected = 20004
Data_Modem_ConnectFail = 20005

LTE_Attach = 20011
LTE_Attach_Request= 20206
LTE_Attach_Accept= 20207
LTE_Attach_Complete= 20208
LTE_Attach_Reject= 20209
LTE_Attach_duration = 20012
LTE_Detach = 20013
LTE_Detach_Request = 20210
LTE_Detach_Accept = 20211
LTE_Detach_Duration= 10202

LTE_TAU = 20014
LTE_TAU_Request = 20212
LTE_TAU_Accept = 20213
LTE_TAU_Complete = 20075
LTE_TAU_Reject = 20214

LTE_Service_Reject = 20015
LTE_Authen = 20016
LTE_Service_Request = 20017
MobilityFromEUTRA = 20018
LTE_Handover_Command = 20019
LTE_Handover_Complete = 20020
LTE_Handover_Fail = 20021
LTE_CSFB_Attempt = 20022
LTE_ExtendedServiceRequest = 20023
LTE_Redirection = 20024
WCDMA_Redirection = 20025

LTE_RACH_Access_Start = 20027
LTE_RACH_Access_Result = 20028
LTE_RACH_RAID_Match = 20029

LTE_Camped_Cell_Status = 20030
LTE_Cell_Resel_Fail = 20031
LTE_Cell_Resel_Start = 20032
LTE_Handover_Failure = 20033
LTE_New_Cell_Ind = 20034
WCDMA_InterFreq_Hard_Handover_Status= 20035
WCDMA_Reselection_End = 20036
WCDMA_Reselection_Start = 20037
LTE_PRACH_MSG1 = 20038
LTE_PRACH_MSG2 = 20039
LTE_PRACH_MSG3 = 20040
LTE_PRACH_MSG4 = 20041

LTE_RRC_IRAT_Resel_From_EUTRAN = 20042
LTE_RRC_IRAT_Resel_From_EUTRAN_Failure = 20043
LTE_RRC_IRAT_Resel_From_EUTRAN_Start = 20044
LTE_RRC_IRAT_Resel_From_EUTRAN_End = 20045
GSM_To_LTE_Resel_Started = 20046
GSM_To_LTE_Resel_Ended = 20047
DS_GSM_to_LTE_Resel_Started = 20048
DS_GSM_to_LTE_Resel_Ended = 20049
GSM_Reselect_End_V2 = 20050
DS_GSM_Reselect_End_V2 = 20051
WCDMA_To_LTE_Reselection_Start_Extended = 20052
GSM_To_WCDMA_Handover_Start = 20053
GSM_Cell_Selection_Start = 20054
GSM_Cell_Selection_End = 20055
WCDMA_Cell_Selected = 20056
GSM_Cell_Selected = 20057
LTE_RRC_Cell_Resel_Failure = 20058
WCDMA_to_LTE_Reselection_End = 20059
WCDMA_to_GSM_Reselection_Start = 20060
WCDMA_to_GSM_Reselection_End = 20061
GSM_to_WCDMA_Reselect_End = 20062

LTE_RRC_NEW_CELL_IND = 20063
LTE_RRC_NEW_CELL_IND_EXT_EARFCN = 20064
IRAT_Reselection = 20065

LTE_Cell_Reselection = 20066
LTE_Cell_Reselection_Intrafreq = 20080
LTE_Cell_Reselection_Interfreq = 20081
LTE_Cell_Reselection_FDD_TO_TDD = 20067
LTE_Cell_Reselection_TDD_TO_FDD = 20068

LTE_Handover_Command_Intrafreq = 20069
LTE_Handover_Complete_Intrafreq = 20070
LTE_Handover_Fail_Intrafreq = 20071

LTE_Handover_Command_Interfreq = 20072
LTE_Handover_Complete_Interfreq = 20073
LTE_Handover_Fail_Interfreq = 20074

LTE_Handover_Command_FDD_TO_TDD = 20087
LTE_Handover_Complete_FDD_TO_TDD = 20082
LTE_Handover_Fail_FDD_TO_TDD = 20083

LTE_Handover_Command_TDD_TO_FDD = 20084
LTE_Handover_Complete_TDD_TO_FDD = 20085
LTE_Handover_Fail_TDD_TO_FDD = 20086


LTE_NB_RACH_MSG1 = 20076
LTE_NB_RACH_MSG2 = 20077
LTE_NB_RACH_MSG3 = 20078
LTE_NB_RACH_MSG4 = 20079


Data_HTTP_Send_Header_Request = 20101
Data_HTTP_Header_Recieved = 20102
Data_FTP_DL_Server_Connecting = 20103
Data_FTP_DL_Server_Connected = 20104
Data_First_Byte_Recieved = 20105
Data_Last_Byte_Recieved = 20106
Data_First_Byte_Sent = 20107
Data_Last_Byte_Sent = 20108
Data_FTP_UL_Server_Connecting = 20109
Data_FTP_UL_Server_Connected = 20110

Data_Connection_Fail = 20201
Data_Download_Timeout = 20202
Data_Upload_Timeout = 20203
Data_Download_Fail = 20204
Data_Upload_Fail = 20205


MeasurementMode= 30400
BECRouterConnectInfo= 30401


Call_Init = 10001
Call_Confirmed = 10002
Call_Setup = 10004
Call_Established = 10005
Call_End = 10006
Call_Setup_Timeout = 10007
Call_Block = 10008
Call_Drop = 10009
Call_Answer_Timeout= 10035
Volte_Call_Init = 10036
Volte_Call_Setup = 10037
Volte_Call_Established = 10038
Volte_Call_End = 10039
Volte_Call_Setup_Timeout = 10040
Volte_Call_Answer_Timeout= 10041
Volte_Call_Block = 10042
Volte_Call_Drop = 10043


MT_Call_Setup = 10024
MT_Call_Initiation = 10025
MT_Call_End = 10026
MT_Call_Drop = 10027
MT_Call_Block = 10028
MT_Call_Confirmed = 10029
MT_Call_Ringing = 10030
MT_Call_Answer = 10031
MT_Call_Established = 10032

MT_VoLTE_Call_Initiation = 10200
MT_VoLTE_Call_Setup = 10201


video_call_init = 10044

SMS_Send = 10019
SMS_Send_Success = 10020
SMS_Send_Fail = 10021
SMS_Delivery_Success = 10022
SMS_Delivery_Fail = 10023


MMS_Send = 20601
MMS_Send_Data_Transfer = 20602
MMS_Send_Success = 20603
MMS_Send_Fail = 20604
MMS_AP_Enabling = 20605
MMS_AP_Enabled = 20606
MMS_AP_Enable_Fail = 20607
MMS_AP_Disabled = 20608


Ftp_Download_Server_Connecting = 20701
Ftp_Download_Server_Connected = 20702
Ftp_Download_First_Byte_Received = 20704
Ftp_Download_Last_Byte_Received = 20705
Ftp_Download_Fail = 20706
Ftp_Download_Timeout = 20707


Ftp_Upload_Server_Connecting = 20751
Ftp_Upload_Server_Connected = 20752
Ftp_Upload_First_Byte_Sent = 20754
Ftp_Upload_Last_Byte_Sent = 20755
Ftp_Upload_Fail = 20756
Ftp_Upload_Timeout = 20757


Http_Download_Server_Connecting = 20801
Http_Download_Server_Connected = 20802
Http_Download_First_Byte_Received = 20804
Http_Download_Last_Byte_Received = 20805
Http_Download_Fail = 20806
Http_Download_Timeout = 20807


Http_Upload_Server_Connecting = 20851
Http_Upload_Server_Connected = 20852
Http_Upload_First_Byte_Sent = 20853
Http_Upload_Last_Byte_Sent = 20854
Http_Upload_Fail = 20855
Http_Upload_Timeout = 20856

Browse_Connecting =  20301
Browse_Connected =  20302
Browse_Connect_Fail =  20303
Browse_Loading_Html =  20304
Browse_Load_Html_Success =  20305
Browse_Load_Html_Fail =  20306
Browse_Load_Timeout =  20307
Browse_Load_Resources_Success =  20308
Browse_Load_Resources_Fail =  20309
Browse_Fail =  20312

YouTube_Loading= 20401
YouTube_Loaded= 20402
YouTube_Video_Start= 20403
YouTube_Video_Buffering= 20404
YouTube_Video_Not_Buffering= 20405
YouTube_Video_Playing= 20406
YouTube_Video_Stopped= 20407
YouTube_Video_Ended= 20408
YouTube_Timeout= 20409
YouTube_Error= 20410
Youtube_Video_Quality= 20411

youtube_upload_video_start= 20412
youtube_upload_video_success= 20413
youtube_upload_video_failed= 20414
youtube_upload_video_timeout= 20415

Waiting_For_New_Sector_Start= 20430
New_Sector_Recording_Start= 20431

Switch_Indoor_Outdoor= 20432
Waiting_For_Switch_Indoor_Outdoor= 20433

video_statement_start= 20441
video_statement_stop= 20442
video_loading= 20443
video_manifest_loaded= 20444
video_play= 20445
video_total_duration_set= 20446
video_playing= 20447
video_waiting= 20448
video_error= 20449
video_end= 20450
video_quality_change= 20451
video_timeout= 20452
video_player_interrupted= 20453
video_fatal_error= 20454


Wifi_Authenticating = 20501
Wifi_Blocked = 20502
Wifi_Connected = 20503
Wifi_Connecting = 20504
Wifi_Disconnected = 20505
Wifi_Disconnecting = 20506
Wifi_Failed = 20507
Wifi_Idle = 20508
Wifi_ObtainingIpAddr = 20509
Wifi_Scanning = 20510
Wifi_Suspended = 20511
Wifi_Enabling = 20512
Wifi_Enabled = 20513
Wifi_Disabling = 20514
Wifi_Disabled = 20515
Wifi_State_Unknown = 20516

wifi_statement_start = 20520
wifi_statement_success = 20521
wifi_statement_failed = 20522

supplicant_state_change = 20531
supplicant_error = 20532
supplicant_connection_change = 20533

Ping_Start = 20651
Ping_Done = 20652
Ping_Success = 20655
Ping_Fail = 20656

Traceroute_Start = 20653
Traceroute_Done = 20654

Ookla_Speedtest_Start = 20660
Ookla_Speedtest_Done = 20661
Processed_Ookla_Speedtest_Fail_Not_Installed= 48
Processed_Ookla_Speedtest_Timeout= 49
Processed_Ookla_Speedtest_OnPause= 50


Dropbox_Authentication_Success = 20680
Dropbox_Authentication_Fail = 20681

Dropbox_Download_Attempt = 20682
Dropbox_Download_First_Byte_Received = 20684
Dropbox_Download_Last_Byte_Received = 20685
Dropbox_Download_Success = 20686
Dropbox_Download_Fail = 20687

Dropbox_Upload_Attempt = 20688
Dropbox_Upload_First_Byte_Sent = 20690
Dropbox_Upload_Last_Byte_Sent = 20691
Dropbox_Upload_Success = 20692
Dropbox_Upload_Fail = 20693


Line_Send = 30001
Line_Send_Result = 30002
Line_Read_Result = 30003
Line_Error = 30004
Line_Recv= 30005
Line_Version= 30006
Line_Photo_Result= 30007
Processed_Line_Send_Message= 15
Processed_Line_Send_Message_Success= 16
Processed_Line_Send_Message_Fail= 17
Processed_Line_Read_Message= 18
Processed_Line_Unread_Message= 19
Processed_Line_Recv_Message= 20
Processed_Line_Send_Sticker= 21
Processed_Line_Send_Sticker_Success= 22
Processed_Line_Send_Sticker_Fail= 23
Processed_Line_Read_Sticker= 24
Processed_Line_Unread_Sticker= 25
Processed_Line_Recv_Sticker= 26
Processed_Line_Send_Photo= 27
Processed_Line_Send_Photo_Success= 28
Processed_Line_Send_Photo_Fail= 29
Processed_Line_Read_Photo= 30
Processed_Line_Unread_Photo= 31
Processed_Line_Recv_Photo= 32
Processed_Line_Photo_Success= 33
Processed_Line_Photo_Timeout= 34
Processed_Line_No_Sending_Event= 44
Processed_Line_Send_Message_Error_Message_Type= 45
Processed_Line_Send_Sticker_Error_Message_Type= 46
Processed_Line_Send_Photo_Error_Message_Type= 47

Line_Call_Init= 30008
Line_Call_Established= 30009
Line_Call_End= 30010
Line_Call_Drop= 30011
Line_Call_Block= 30012
Line_Call_Normal_Clearing= 30013
Line_Call_No_Answer= 30014
Line_Call_State_Error= 30015

Line_Call_Answered= 30017
Line_Answer_Call_Drop= 30018
Line_Call_Dial= 30019
Line_Answer_Call_End= 30020



Facebook_Post_Status = 30051
Facebook_Post_Status_Success = 30052
Facebook_Post_Status_Fail = 30053
Facebook_Post_Photo = 30054
Facebook_Post_Photo_Success = 30055
Facebook_Post_Photo_Fail = 30056
Facebook_Download_Photo = 30057
Facebook_Download_Photo_Start = 30058
Facebook_Download_Photo_First_Byte_Received = 30059
Facebook_Download_Photo_Last_Byte_Received = 30060
Facebook_Download_Photo_Success = 30061
Facebook_Download_Photo_Fail = 30062
Facebook_Download_Photo_Timeout = 30063
Facebook_Post_Photo_Start = 30064
Facebook_Post_Status_Timeout = 30065
Facebook_Post_Photo_Timeout = 30066
Facebook_Post_Status_Start = 30067


Instagram_Download_Photo = 30101
Instagram_Download_Photo_First_Byte_Received = 30102
Instagram_Download_Photo_Last_Byte_Received = 30103
Instagram_Download_Photo_Success = 30104
Instagram_Download_Photo_Fail = 30105
Instagram_Download_Photo_Timeout = 30106

instagram_post_photo_start = 30111
instagram_post_photo_success = 30112
instagram_post_photo_failed = 30113
instagram_post_photo_timeout = 30114


Email_Send_Start  = 30151
Email_Send_Success  = 30152
Email_Send_Fail  = 30153
Email_Authentication_Fail = 30154
Email_Authentication_Seccess = 30155
Email_Unknow_Host = 30156
Email_Send_Timeout = 30157
Email_Set_SMTP_Server_Properties_Start = 30158
Email_Set_SMTP_Server_Host_Start = 30159
Email_Set_SMTP_Server_Host_Success = 30160
Email_Set_Sender_User_Start = 30161
Email_Set_Sender_User_Success = 30162
Email_Set_Sender_Password_Start = 30163
Email_Set_Sender_Password_Success = 30164
Email_Set_SMTP_Port_Start = 30165
Email_Set_SMTP_Port_Success = 30166
Email_Set_SMTP_SSL_Trust_Start = 30167
Email_Set_SMTP_SSL_Trust_Success = 30168
Email_Set_Timeout_Start = 30169
Email_Set_Timeout_Success = 30170
Email_Set_SMTP_Server_Properties_Success = 30171
Email_Create_Sending_Session_Start = 30172
Email_Create_Sending_Session_Success = 30173
Email_Create_Email_Message_Start = 30174
Email_Create_Email_Message_Success = 30175
Email_Lookup_SMTP_Server_IP_Start = 30176
Email_Lookup_SMTP_Server_IP_Success = 30177
Email_Create_Receiver_IP_Object_Start = 30178
Email_Create_Receiver_IP_Object_Success = 30179
Email_Transfer_IP_Object_To_IP_Address_Start = 30180
Email_Transfer_IP_Object_To_IP_Address_Success = 30181
Email_Send_Message_Start = 30182
Email_Send_Message_Success = 30183
Email_IP_Address_Fail = 30184
Email_Message_Fail = 30185
Email_Other_Fail= 30186
Email_Create_File_Start= 30187
Email_Create_File_success = 30188
Email_Create_File_Fail = 30189


Wait_Start = 30251
Wait_End = 30252


DNSLookup = 30300
DNSLookup_IP_Success= 30301
DNSLookup_IP_Fail= 30302
DNSLookup_IP_Timeout= 30303


Image_Processing_Engine_Fail= 30350
component_load_start= 30360
component_ready= 30361
component_load_failed= 30362

whatsapp_send_message_start= 30551
whatsapp_send_message_success= 30552
whatsapp_send_message_fail= 30553
whatsapp_send_message_timeout= 30554


iperf3_result= 30601
iperf2_result= 30602


ussd_request_start= 30611
ussd_request_success= 30612
ussd_request_failed= 30613
ussd_request_end= 30614


request_report_per_cell= 31001


Dynamic_Cellfile_Data= 31021


at_device_attached= 40001
at_device_detached= 40002
at_device_connection_state_change= 40003
at_device_event= 40004
at_cmd_tx= 40005
at_cmd_rx= 40006


ls_ping_start= 41001
ls_ping_done= 41002


ui_automator_test_start= 41011
ui_automator_test_stop= 41012
ui_automator_test_error= 41013


tcpdump_dns_query_request= 100001
tcpdump_dns_query_response= 100002
tcpdump_syn= 100003
tcpdump_syn_ack= 100004


plugin_start= 110000
plugin_stop= 110001


plugin_tshark_start= 111000
plugin_tshark_stop= 111001
plugin_tshark_ports= 111002
plugin_tshark_save_format= 111003
plugin_tshark_file_prefix= 111004


plugin_tshark_subplugin_eap_analysis_start= 111100
plugin_tshark_subplugin_eap_analysis_stop= 111101
plugin_tshark_subplugin_eap_analysis_failed= 111102
plugin_tshark_subplugin_eap_analysis_authen_start_datetime= 111103
plugin_tshark_subplugin_eap_analysis_dhcp_offer_datetime= 111104
plugin_tshark_subplugin_eap_analysis_dhcp_ack_datetime= 111105
plugin_tshark_subplugin_eap_analysis_captive_portal_dns_req_datetime= 111106
plugin_tshark_subplugin_eap_analysis_captive_portal_dns_res_datetime= 111107
plugin_tshark_subplugin_eap_analysis_captive_portal_http_req_datetime= 111108
