from tkinter import *
from datetime import *
import random
import time
import threading
from tkinter import messagebox
import pymysql
import sqlite3

import tkinter.font
from functools import partial

class MainClass(Tk):
    
    def __init__(self, temp_mnum, *args, **kwargs):
        self.mnum = temp_mnum
        
        Tk.__init__(self, *args, **kwargs)
        
        self.title("MMP")
        self.geometry("800x800")
        
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (ReservationPage, MyPage, ManagerLoginPage, ManagerPage):       
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("ReservationPage")
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def destroy_frame(self):
        self.destroy()
        LoginPage()

#-------------------------------------------------------------#       
#-------------------- 수업조회 및 예약  페이지 --------------------#
#-------------------------------------------------------------# 
class ReservationPage(Frame):
    
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller

        # 프레임 전환 메뉴
        mb=Menu(self.controller)
        mb.add_command(label="수업조회", command=lambda: self.controller.show_frame("ReservationPage"))
        mb.add_command(label="마이페이지", command=lambda: self.controller.show_frame("MyPage"))
        mb.add_command(label="관리자페이지", command=lambda: self.controller.show_frame("ManagerLoginPage"))
        self.controller.config(menu=mb)
                
        
        #제목 label 설정
        fontText=tkinter.font.Font(size=15, weight="bold")
        label1 = Label(self, text="수업 예약 페이지 입니다." + "\n" + "예약/ 취소 하시려는 수업을 클릭 해 주세요!", font = fontText)
        label2 = Label (self, text= "(단, 취소는 하루 전 까지, 예약은 1주일 이내의 수업만 가능합니다.)" , fg = "red")
        label1.grid(row=0 , column = 0,pady =10, padx =10)
        label2.grid(row=1 ,column = 0 ,pady =10, padx =10)
        self.userNum = self.controller.mnum #임시로 **추후변경**

        #db 연결
        conn = sqlite3.connect("mmp.db")
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
        # SQL문 실행 - 오늘로부터 7일 이내의 수업 조회
        sql = "select c.cnum , c.cname, c.ccontent, c.ctime, count(s.cnum) nowNum, c.cmax from class c left join sugan s  on c.cnum = s.cnum where CAST(strftime('%s', c.ctime) AS integer ) > CAST(strftime('%s', datetime('now','localtime')) AS integer ) and CAST(strftime('%s', c.ctime) AS integer ) < CAST(strftime('%s', datetime('now','localtime','+7 day')) AS integer )  group by c.cnum"
        curs.execute(sql)
        # 데이타 Fetch
        self.rows = StringVar()
        self.rows = curs.fetchall()
        # Connection 닫기
        conn.close()

        #Label, Frame, Button 변수 초기화
        self.cnum = {}
        self.date = {}
        self.name = {}
        button_identities  =[]
        self.btn ={}
        self.nowNum = {}
        self.timeLabel = {}
        self.classFrame  = {}
        self.numberLabel ={}
        #db에서 select 결과의 갯수 만큼 실행 
        for i in range(0,len(self.rows)):
            #sql문 select 결과를 이용해서 화면에 출력해줄 형태로 변환
            index = i
            self.cnum[i] = self.rows[i][0]
            self.name[i] = self.rows[i][1]
            content = self.rows[i][2]
            self.date[i] = self.rows[i][3]
            self.nowNum[i] = str(self.rows[i][4])
            maxNum = str(self.rows[i][5])
            strTime =  "수업 시간: \n " + self.date[i] 
            strClass = "강좌 : " + self.name[i]+ "\n 내용 : " + content
            strNum =  "신청 현황  \n" + str(self.nowNum[i]) + "/" + maxNum
            if self.isMyClass(self.userNum , self.cnum[i]):
                btnColor = "white"
            else:
                btnColor = "green"
            if int(self.nowNum[i]) == 6  :
               strColor = "red"
            else:
                strColor = "blue" 
            #각 수업에 대한 Button, Label들 정의
            self.classFrame[i] = Frame(self, relief="solid")
            self.classFrame[i].grid(row = i+2, column= 0, pady =10)
            self.timeLabel[i] = Label ( self.classFrame[i], text = strTime)
            self.timeLabel[i].grid(row=0, column=0)
            self.numberLabel[i] = Label ( self.classFrame[i], text = strNum, fg = strColor)
            self.numberLabel[i].grid(row=0, column=2)
            #버튼을 클릭했을 때 i값을 전달하면서 applyCancel() 함수 실행
            self.btn [i] = Button( self.classFrame[i], text = strClass, bg = btnColor ,padx =10 ,pady = 15 , command = partial(self.applyCancel, i))
            self.btn [i].grid(row=0, column=1)
        
        logoutBtn = Button(self, text = "로그아웃 하기",
                          command=controller.destroy_frame)
        logoutBtn.grid(row = 5 + len(self.rows), column =0)



    #수업 예약, 취소 함
    def applyCancel(self, n):
        classNum = str(self.cnum[n])
        now = int(self.nowNum[n])
        conn =sqlite3.connect("mmp.db")
        curs = conn.cursor()
        sql = "SELECT * FROM sugan where mnum = "+ str(self.userNum) +" and cnum ="+classNum+";"
        curs.execute(sql)
        rows = curs.fetchall()
        
        #사용자가  예약한 수업일 경우 취소 여부 묻고 실행
        if len(rows) :
            strInfo = self.name[n] + "를 취소하시겠습니까? \n" + "시간 : " + self.date[n]
            isCancel =  messagebox.askokcancel("취소 창", strInfo)
            if isCancel:
                sql = "delete from sugan where mnum = "+ str(self.userNum)+ " and cnum = " + classNum + ";"
                curs.execute(sql)
                conn.commit()
                self.refresh()
                self.controller.show_frame("ReservationPage")
      
        #새로 예약하는 경우 
        else :
            #정원 체크
            sql ="select count(s.cnum) nowNum from class c left join sugan s  on c.cnum = s.cnum where c.cnum = "+classNum +" group by c.cnum"
            curs.execute(sql)
            row = curs.fetchone()
            now = row[0]
            if int(now)==6:
                messagebox.showinfo("정원 초과", "정원이 초과했습니다. 다른 수업을 이용해 주시면 감사하겠습니다.")
                return
            strInfo = self.name[n] + "를 예약하시겠습니까? \n" + "시간 : " + self.date[n]
            isReserve = messagebox.askokcancel("예약 창", strInfo)
            if isReserve:
                sql = "insert into sugan  (mnum, cnum) values ("+str(self.userNum) +","+ classNum +");"
                curs.execute(sql)
                conn.commit()
                self.refresh()
                self.controller.show_frame("ReservationPage")
      
        # Connection 닫기
        conn.close()
        
    #내가 신청한 수업인지 아닌지 체크  
    def isMyClass(self, mnum, cnum):
        conn = sqlite3.connect("mmp.db")
        curs = conn.cursor()
        sql ="select c.cnum from class c, sugan s where c.cnum = s.cnum and c.cnum = "+str(cnum)+" and s.mnum = "+str(mnum)+" and  CAST(strftime('%s', c.ctime) AS integer ) > CAST(strftime('%s', datetime('now','localtime')) AS integer ) and CAST(strftime('%s', c.ctime) AS integer ) < CAST(strftime('%s', datetime('now','localtime','+7 day')) AS integer ) "
        curs.execute(sql)
        rows = curs.fetchall()
        conn.close()
        if len(rows) == 0:
            return False
        else:
            return True           

    #예약/취소후 화면을 새로 고침하는 함수   
    def refresh(self):
        conn =sqlite3.connect("mmp.db")
        curs = conn.cursor()
        sql = "select c.cnum , c.cname, c.ccontent, c.ctime, count(s.cnum) nowNum, c.cmax from class c left join sugan s  on c.cnum = s.cnum where CAST(strftime('%s', c.ctime) AS integer ) > CAST(strftime('%s', datetime('now','localtime')) AS integer ) and CAST(strftime('%s', c.ctime) AS integer ) < CAST(strftime('%s', datetime('now','localtime','+7 day')) AS integer )  group by c.cnum"
        curs.execute(sql)
        self.rows = curs.fetchall()

        for i in range(0,len(self.rows)):            
            nowNum = str(self.rows[i][4])
            maxNum = str(self.rows[i][5])
            strNum =  "신청 현황  \n" + nowNum + "/" + maxNum
            classNum = self.rows[i][0]
            if self.isMyClass(self.userNum, classNum):
                btnColor = "white"
            else:
                btnColor = "green"
            if int(nowNum) == 6  :
               strColor = "red"
            else:
                strColor = "blue"
            #configure 이용해서 Button, Label 상태 update    
            self.numberLabel[i].configure(text = strNum, fg = strColor)
            self.btn[i].configure(bg = btnColor)
        conn.close()      

    
#---------------------------------------------------------

#-------------------- 관리자 페이지 --------------------
class ManagerLoginPage(Frame):    
    ##관리자 로그인 페이지 프레임
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller

        ###mngpw : 관리자 비밀번호
        self.mngpw="password"

        Label(self, text="관리자 비밀번호", padx=15, pady=10).grid(row=0, column=0, sticky="W")

        ###mngpwSV : 입력한 관리자 비밀번호
        self.mngpwSV = StringVar()
        ###mngpwE : 관리자 비밀번호 입력 Entry
        self.mngpwE = Entry(self, show="*", textvariable=self.mngpwSV)
        self.mngpwE.grid(padx=15, row=1, column=0)
        ###trymnglog : 관리자 로그인 초기화
        self.trymnglog=-1
        self.mngpwE.bind("<Return>", self.bemng)

        ###mnglogB : 관리자 로그인 버튼
        mnglogB = Button(self, text="입력", width=5, command=self.mnglog)
        mnglogB.grid(row=1, column=1)


    ##bemng : 관리자 로그인 시도(enter) 함수
    def bemng(self, event):
        ###관리자 로그인 시도 중
        self.trymnglog=0
        if(self.trymnglog==0):
            self.mnglog()
            ###trymnglog : 관리자 로그인 초기화
            self.trymnglog=-1

    ##mnglog : 관리자 로그인 함수
    def mnglog(self):
        print("관리자 로그인", self.mngpwSV.get())
        ###관리자 비밀번호와 입력한 관리자 비밀번호가 같으면 로그인 성공
        if(self.mngpw==str(self.mngpwSV.get())):
            ####Entry에 입력한 내용 초기화
            self.mngpwE.delete(0,END)
            ####관리자 페이지 열기
            self.controller.show_frame("ManagerPage")
        ###로그인 실패
        else:
            ####실패 메세지박스 보이기
            messagebox.showinfo("information", "비밀번호가 틀렸습니다.")
            ####Entry에 입력한 내용 초기화
            self.mngpwE.delete(0,END)

class ManagerPage(Frame):
    ##관리자 페이지 프레임
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        ####tryadd : 수업/회원 등록 프레임 초기화
        self.tryadd=-1
        self.tryaddClass()

        ###addcpB/addmpB : 회원/수업 등록 프레임 변경 라디오 버튼
        self.addcpRB = Radiobutton(self, text="수업등록", value=0, command=self.tryaddClass)
        self.addcpRB.grid(row=0, column=0, sticky="W")
        self.addmpRB = Radiobutton(self, text="회원등록", value=1, command=self.tryaddMember)
        self.addmpRB.grid(row=0, column=0)
        ###mnglogoutB : 관리자 로그아웃 버튼
        mnglogoutB = Button(self, text="관리자 로그아웃",
                            command=lambda: self.controller.show_frame("ManagerLoginPage"))
        mnglogoutB.grid(row=2, column=0, sticky="E", pady=70)
    
    ##tryaddClass : 수업 등록 프레임
    def tryaddClass(self):
        ###수업 등록 중
        self.tryadd=0
        ###addcF : 수업 등록 프레임
        self.addcF = Frame(self)
        self.addcF.grid(row=1, column=0)

        ###cName : 수업이름
        Label(self.addcF, text="이　름", padx=20).grid(row=1, column=0)
        self.cName = Entry(self.addcF)
        self.cName.grid(row=1, column=1)

        ###cDate : 수업날짜
        Label(self.addcF, text="날　짜", padx=20).grid(row=2, column=0)
        self.cDate1 = Entry(self.addcF, width=5)
        self.cDate1.grid(row=2, column=1, sticky="W")
        self.cDate2 = Entry(self.addcF, width=5)
        self.cDate2.grid(row=2, column=1)
        self.cDate3 = Entry(self.addcF, width=5)
        self.cDate3.grid(row=2, column=1, sticky="E")

        ###mLimit : 수업인원
        Label(self.addcF, text="인　원", padx=20).grid(row=3, column=0)
        self.mLimit = Entry(self.addcF)
        self.mLimit.grid(row=3, column=1)

        ###addcB : 수업등록 버튼
        addcB = Button(self.addcF, text="등록", command=self.addClick, width=5)
        addcB.grid(row=7, column=1, sticky="E", pady=5)
        
    ##tryaddMember : 회원 등록 프레임
    def tryaddMember(self):
        ###회원 등록 중
        self.tryadd=1
        ###addmF : 회원 등록 프레임
        self.addmF = Frame(self)
        self.addmF.grid(row=1, column=0)

        ###mbNae : 회원이름
        Label(self.addmF, text="이　름", padx=20).grid(row=1, column=0)
        self.mbName = Entry(self.addmF)
        self.mbName.grid(row=1, column=1)

        ###mbNum : 회원번호
        Label(self.addmF, text="번　호", padx=20).grid(row=2, column=0)
        self.mbNum1 = Entry(self.addmF, width=5)
        self.mbNum1.grid(row=2, column=1, sticky="W")
        self.mbNum2 = Entry(self.addmF, width=5)
        self.mbNum2.grid(row=2, column=1)
        self.mbNum3 = Entry(self.addmF, width=5)
        self.mbNum3.grid(row=2, column=1, sticky="E")

        ###rTime : 잔여횟수
        Label(self.addmF, text="횟　수", padx=20).grid(row=3, column=0)
        self.rTime = Entry(self.addmF)
        self.rTime.grid(row=3, column=1)

        ###addmB : 회원등록 버튼
        addmB = Button(self.addmF, text="등록", command=self.addClick, width=5)
        addmB.grid(row=4, column=1, sticky="E", pady=5)

    ##addClick : 등록 버튼 클릭 함수
    def addClick(self):
        ###등록 질문 메세지박스
        if (messagebox.askokcancel("Redirecting", "등록하시겠습니까?")):
            ###확인 버튼 클릭 시
            ####데이터베이스 연결
            self.conn=pymysql.connect(host="127.0.0.1", user="root", passwd="0000", db="mmp")
            self.cur = self.conn.cursor()
            ####입력 내용 오류 확인 및 등록
            if (self.tryadd==0):
                if(len(self.cDate1.get())!=4 or (int(self.cDate2.get())<1 or int(self.cDate2.get())>12) or (int(self.cDate3.get())<1 or int(self.cDate3.get())>31)) :
                    messagebox.showinfo("information","등록 실패")
                else:self.addClass()
            elif (self.tryadd==1):
                if(str(self.mbNum1.get())!="010" or (len(self.mbNum2.get()) and len(self.mbNum3.get()))!=4):
                    messagebox.showinfo("information","등록 실패")
                else:self.addMember()
            ###데이터베이스 닫기
            self.conn.close()
                
    ##addClass : 수업등록 함수
    def addClass(self):
        try :
            sql = "INSERT INTO class(cname, cdate, mlimit) VALUES (%s, %s, %s)"
            val=(str(self.cName.get()), str(self.cDate1.get())+"/"+str(self.cDate2.get())+"/"+str(self.cDate3.get()), int(self.mLimit.get()))
            print(val)
            self.cur.execute(sql,val)
            print("수업등록:", val)
            self.conn.commit()
            ###Entry에 입력한 내용 초기화
            self.cName.delete(0,END)
            self.cDate1.delete(0,END)
            self.cDate2.delete(0,END)
            self.cDate3.delete(0,END)
            self.mLimit.delete(0,END)
        except :
            self.conn.rollback()
            messagebox.showinfo("information","등록 실패")  

    ##addMember : 회원등록 함수
    def addMember(self):
        ###SQL문 실행
        try :
            sql = "INSERT INTO member(mname, mnum, rtime) VALUES (%s, %s, %s)"
            val=(str(self.mbName.get()), str(self.mbNum1.get())+str(self.mbNum2.get())+str(self.mbNum3.get()), int(self.rTime.get()))
            self.cur.execute(sql,val)
            self.conn.commit()
            ###Entry에 입력한 내용 초기화
            self.mbName.delete(0,END)
            self.mbNum1.delete(0,END)
            self.mbNum2.delete(0,END)
            self.mbNum3.delete(0,END)
            self.rTime.delete(0,END)
        ###데이터 입력 실패
        except :
            self.conn.rollback()
            messagebox.showinfo("information","등록 실패")  

    ##mnglogout : 관리자 페이지 로그아웃 함수
    def mnglogout(self):
        ###프레임 초기화
        self.resetmn()
        self.tryadd=-1
        ###페이지 이동
        self.controller.show_frame("ReservationPage")
#----------------------------------------------------------

#---------------------------------------------------------#       
#---------------------- 마이페이지 -----------------------#
#---------------------------------------------------------# 
class MyPage(Frame):
    
    def __init__(self, parent, controller):
        
        Frame.__init__(self, parent)
        self.controller = controller

        # DB 연결
        conn = sqlite3.connect("mmp.db")
        
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
 
        # SQL문 실행
        sql = "select mname from member where mnum = " + str(self.controller.mnum) + ";"
        curs.execute(sql)
 
        # 데이타 Fetch
        rows = curs.fetchall()

        # Connection 닫기
        conn.close()


        # 'XX님의 페이지'라는 라벨 출력
        font1 = tkinter.font.Font(size=15, weight="bold")
        label = Label(self, text="This is " + rows[0][0] + "'s Page", font=font1)
        label.grid(row=0, column=0, pady=10)

        # bottomWindow라는 프레임 객체 생성
        self.bottomWindow = Frame(self)
        self.bottomWindow.grid(row = 1)  

        # 강좌명 출력
        self.mypage()

        # 버튼
        refreshBtn = Button(self, text="Refresh",
                            command=self.mypage)
        reservationBtn = Button(self, text="Go back",
                            command=lambda: controller.show_frame("ReservationPage"))
        logoutBtn = Button(self, text = "Logout",
                            command=controller.destroy_frame)
        
        refreshBtn.grid(row=len(self.rows) + 2, column=0, pady=5)
        reservationBtn.grid(row=len(self.rows) + 3, column=0, pady=5)
        logoutBtn.grid(row=len(self.rows) + 4, column=0, pady=5)


    # 강좌명 bottomWindow 프레임에 출력
    def mypage(self):

        # DB 연결
        conn = sqlite3.connect("mmp.db")
        
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
 
        # SQL문 실행
        sql = "select c.cname, c.ccontent, strftime('%Y-%m-%d %H:%M', c.ctime), count(s.cnum) nowNum, c.cmax from class c inner join sugan s on c.cnum = s.cnum where c.cnum in(select s.cnum from sugan s where s.mnum =" + str(self.controller.mnum) + ") group by c.cnum order by c.ctime"
        curs.execute(sql)
        
              
        # 데이타 Fetch
        self.rows = curs.fetchall()

        # Connection 닫기
        conn.close()

        # bottomWindow 프레임 비우기
        self.clearBot()

        now = datetime.now()

        # 내가 듣는 수업 출력
        for i in range(0, len(self.rows)):

            # 테스트용
            print(self.rows[i][2])

            if (self.rows[i][2] > str(now)):
                strColor = "blue"
                font2 = tkinter.font.Font(size=10, overstrike=False)
            else:
                strColor = "black"
                font2 = tkinter.font.Font(size=10, overstrike=True)
            date = self.rows[i][2]
            name = self.rows[i][0]
            content = self.rows[i][1]
            nowNum = self.rows[i][3]
            max = self.rows[i][4]

            text1 = date.split(' ')[0] + "\n" + date.split(' ')[1]
            text2 = "강좌명: " + name
            text3 = "신청 현황: " + str(nowNum) + "/" + str(max)
            
            Label(self.bottomWindow, text=text1, font=font2, fg=strColor).grid(row=i + 1, column=0, padx=10, pady=10)
            Label(self.bottomWindow, text=text2, font=font2, fg=strColor).grid(row=i + 1, column=1, padx=10, pady=10)
            Label(self.bottomWindow, text=text3, font=font2, fg=strColor).grid(row=i + 1, column=2, padx=10, pady=10)
        

    # bottomWindow에 생성한 강좌명들 삭제
    def clearBot(self):
        mylist = self.bottomWindow.grid_slaves()
        
        for i in mylist:
            i.destroy()
#---------------------------------------------------------
            
#---------------------------------------------------------#       
#--------------------- 로그인페이지 ----------------------#
#---------------------------------------------------------# 
class LoginPage(Tk):

    def __init__(self):
        self.temp_mnum = 0

        Tk.__init__(self)
        self.title("login")

        # DB 연결
        conn = sqlite3.connect("mmp.db")
        
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
 
        # SQL문 실행
        sql = "select * from member"
        curs.execute(sql)
 
        # 데이타 Fetch
        self.rows = curs.fetchall()
        print(self.rows)                ##### 테스트용

        # Connection 닫기
        conn.close()

        self.name = StringVar()

        # 회원번호를 입력해 달라는 Label
        Label(self, text="회원번호를 입력해주세요.").grid(row=0, padx=10, pady=10)
 
        # 회원번호 입력 Entry
        logID = Entry(self, textvariable=self.name)
        logID.bind("<Return>", self.login)   # 엔터 키
        logID.grid(row=1, padx=10, pady=10)
            
        # 로그인 Button
        btnLogin = Button(self, text="로그인", command=self.login)
        btnLogin.grid(row=2, padx=10, pady=10)


    # 회원번호가 db에 있는지 확인
    def login(self, event=None):
        for i in range(0, len(self.rows)):
            if (str(self.name.get()) == str(self.rows[i][2])):
                self.temp_mnum = self.rows[i][0]
                self.destroy()
                MainClass(self.temp_mnum).mainloop()
                break;
            elif (len(self.rows) - 1 == i):
                messagebox.showwarning("안내", "로그인에 실패하였습니다.")
#---------------------------------------------------------------------------
                
if __name__ == "__main__":
    LoginPage()    
