import os
import re
import time
import shutil
import zipfile
from selenium import webdriver


class ExtensionHelper(object):
    '''Selenium + Chrome 使用用户名密码认证的代理封装'''

    CHROME_PROXY_HELPER_DIR = 'Chrome-proxy-helper'  # Chrome代理模板插件目录
    CUSTOM_CHROME_PROXY_EXTENSIONS_DIR = 'chrome-proxy-extensions'  # 存储自定义Chrome代理扩展文件的目录

    @classmethod
    def create_extension(cls, proxy):
        '''
        创建插件
        :param proxy: username:password@ip:port
        :return:
        '''
        m = re.compile('([^:]+):([^\@]+)\@([\d\.]+):(\d+)').search(proxy)  # 匹配代理格式是否正确
        if m:
            # 提取代理的各项参数
            username = m.groups()[0]
            password = m.groups()[1]
            ip = m.groups()[2]
            port = m.groups()[3]
            # 创建一个定制Chrome代理扩展(zip文件)
            if os.path.exists(cls.CUSTOM_CHROME_PROXY_EXTENSIONS_DIR):
                shutil.rmtree(cls.CUSTOM_CHROME_PROXY_EXTENSIONS_DIR)
            os.mkdir(cls.CUSTOM_CHROME_PROXY_EXTENSIONS_DIR)
            extension_file_path = os.path.join(cls.CUSTOM_CHROME_PROXY_EXTENSIONS_DIR,
                                               '{}.zip'.format(proxy.replace(':', '_')))
            if not os.path.exists(extension_file_path):
                # 扩展文件不存在，创建
                zf = zipfile.ZipFile(extension_file_path, mode='w')
                zf.write(os.path.join(cls.CHROME_PROXY_HELPER_DIR, 'manifest.json'), 'manifest.json')
                # 替换模板中的代理参数
                background_content = open(os.path.join(cls.CHROME_PROXY_HELPER_DIR, 'background.js')).read()
                background_content = background_content.replace('%proxy_host', ip)
                background_content = background_content.replace('%proxy_port', port)
                background_content = background_content.replace('%username', username)
                background_content = background_content.replace('%password', password)
                zf.writestr('background.js', background_content)
                zf.close()
            return extension_file_path
        else:
            raise Exception('代理格式错误: username:password@ip:port')


if __name__ == '__main__':
    # 自定义修改
    user_pass = '201812251154134385:10115029'
    host, port = '115.221.126.154', '22214'

    proxy = '{0}@{1}:{2}'.format(user_pass, host, port)  # 格式：username:password@ip:port
    options = webdriver.ChromeOptions()
    options.add_extension(ExtensionHelper.create_extension(proxy))  # 需要验证(调用封装方法、添加插件)
    # options.add_argument("--proxy-server=http://{}:{}".format(host, port))    # 不需验证
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('http://httpbin.org/ip')  # 访问一个IP回显网站，查看代理配置是否生效了
    time.sleep(10)
    driver.quit()
