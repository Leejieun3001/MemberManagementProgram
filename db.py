import pymysql
'''
#데이터베이스 생성
conn=pymysql.connect(host="127.0.0.1", user="root", passwd="1234")
cur = conn.cursor()

try :
    cur.execute("CREATE DATABASE MMP")
    conn.commit()
except:
    conn.rollback()
finally:
    conn.close()
'''
'''
#테이블 생성
conn = pymysql.connect(host = "127.0.0.1", user = "root",passwd = "1234", db="mmp")    
cur = conn.cursor()

try:
    sql = [ """CREATE TABLE member (
                mnum VARCHAR(11) NOT NULL,
                mname VARCHAR(20) NOT NULL,
                rtime INT(10) NOT NULL,
                PRIMARY KEY(mnum)
            );""",              
        """CREATE TABLE class (
                cname VARCHAR(20) NOT NULL,
                cdate VARCHAR(10) NOT NULL,
                mlimit INT(10) NOT NULL,
                PRIMARY KEY(cdate)
            );""",
        """CREATE TABLE regist (
                seq INT UNSIGNED NOT NULL AUTO_INCREMENT,
                mnum VARCHAR(11) NOT NULL,
                cdate VARCHAR(10) NOT NULL,
                PRIMARY KEY(seq),
                FOREIGN KEY(mnum) REFERENCES member(mnum),
                FOREIGN KEY(cdate) REFERENCES class(cdate)
            );"""]
    for s in sql:
        cur.execute(s)
        conn.commit()
except:
    conn.rollback()
finally:
    conn.close()
'''
'''
conn = pymysql.connect(host = "127.0.0.1", user = "root",passwd = "1234", db="mmp")    
cur = conn.cursor()

try:
    sql = "INSERT INTO member(mname, mnum, mlimit) VALUES (%s, %s, %d)"
    val=("name","123",1)
    print(val)
    cur.execute(sql,val)
    conn.commit()
except :
    conn.rollback()
    print("실패")
finally:
    conn.close()
'''
