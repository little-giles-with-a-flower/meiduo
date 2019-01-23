import random

from django.shortcuts import render

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import constants

# Create your views here.

# 获取短信验证码
# API:GET /sms_codes/（?p<mobile>1[3-9]\d{9}）/
# 参数：
#     通过url传递手机号
class SMSCodeView(APIView):
    def get(self, request, mobile, redis_conn=None):
        """
        获取短信验证码
        """
        # 判断图片验证码, 判断是否在60s内
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            return Response({"message": "请求次数过于频繁"}, status=status.HTTP_400_BAD_REQUEST)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')

        # 创建redis管道对象
        pl = redis_conn.pipeline()

        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 一次执行redis管道的所有命令
        pl.execute()

        # # 发送短信验证码
        # sms_code_expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        # try:
        #   ccp = CCP()
        #   # 调用云通信发送短信验证码
        #   res = ccp.send_template_sms(mobile, [code, expires], SMS_CODE_TEMP_ID)
        # except Exception as e:
        #   return Response({"message": "发送短信异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        #
        # if res != 0:
        #   return Response({"message": "发送短信失败"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 返回应答，短信发送成功
        return Response({"message": "OK"})