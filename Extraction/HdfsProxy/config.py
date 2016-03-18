import base64,os,ConfigParser

os.chdir(os.path.dirname(__file__))


config = ConfigParser.RawConfigParser()
config.read('..\configure')
user_name = raw_input('input the user name:')
user_pwd = raw_input('input the user password:')
if(user_name and user_pwd
    config.set('HDFS', 'user name', base64.encodestring(user_name))
    config.set('HDFS', 'password', base64.encodestring(user_pwd))
    
with open('..\configure', 'wb') as configfile:
    config.write(configfile)
