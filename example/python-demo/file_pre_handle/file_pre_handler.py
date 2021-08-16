from sender.sendRabbitMQTool import sendRabbitMQTool

if __name__ == '__main__':
    a = sendRabbitMQTool('file_cdn_dev', 11)
    with open('C:\\Users\\Administrator\\Documents\\WXWork\\1688850135175963\\Cache\\File\\2021-08\\测试消息——内网_Announmt_Stock(1).txt',
              'r',
              encoding='utf-8') as f1:
        list1 = f1.readlines()
        for list in list1:
            a.send_json(list.replace("\n", ""))
