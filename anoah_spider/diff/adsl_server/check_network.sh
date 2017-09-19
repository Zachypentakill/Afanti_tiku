#!/usr/bin/expect

spawn ssh "root@118.119.102.51" -p "20323" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@221.10.101.121" -p "21121" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@113.59.34.53" -p "20139" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@157.122.243.163" -p "20353" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@183.131.135.221" -p "20481" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@60.18.149.249" -p "20070" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@222.174.243.58" -p "20202" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@61.154.198.82" -p "20412" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@114.104.160.180" -p "20552" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}

spawn ssh "root@61.132.72.163" -p "20392" "curl -s baidu.com"
expect {
    assword: {
        send "pwd\r"
    }
}
interact {}
