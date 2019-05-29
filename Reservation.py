from tkinter import *
from datetime import *
import random
import time
import threading
from tkinter import messagebox
import pymysql
import tkinter.font

MNGTITLE="관리자 페이지"

#-------------------- 메인 --------------------
class MainClass(Tk):
    def __init__(self):
        Tk.__init__(self)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (LoginPage,ReservationPage, MyPage):       
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
#-------------------- 수업조회 페이지 --------------------
class ReservationPage(Frame):
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        t = ['월', '화', '수', '목', '금', '토', '일']
        self.controller = controller
        fontText=tkinter.font.Font(size=20, weight="bold")
        label1 = Label(self, text="수업 예약 페이지 입니다." + "\n" + "예약/ 취소 하시려는 수업을 클릭 해 주세요!", font = fontText)
        label2 = Label (self, text= "(단, 취소는 하루 전 까지, 예약은 1주일 이내의 수업만 가능합니다.)" , fg = "red")
        label1.pack(side="top", fill="x", pady=10)
        label2.pack(side="top", fill="x")
        
        
        conn = pymysql.connect(host = 'localhost', user = 'root', password = '1234' ,db = 'MMP')
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
 
        # SQL문 실행
        sql = "select c.cnum , c.cname, c.ccontent, c.ctime, count(s.cnum) nowNum, c.cmax from mmp.class c left join mmp.sugan s  on c.cnum = s.cnum where ctime > sysdate() and ctime < date_add(now(), interval +7 day) group by c.cnum"
        curs.execute(sql)
 
        # 데이타 Fetch
        rows = curs.fetchall()
        print(rows)     # 전체 rows
        # print(rows[0])  # 첫번째 row: (1, '김정수', 1, '서울')
        # print(rows[1])  # 두번째 row: (2, '강수정', 2, '서울')
        # Connection 닫기
        conn.close()

        for i in range(0,len(rows)):
            name = rows[i][1]
            content = rows[i][2]
            date = rows[i][3].strftime('%Y년 %m월 %d일 - %H시 %M분')

            nowNum = str(rows[i][4])
            maxNum = str(rows[i][5])
            strClass = "강좌 : " + name+ " 내용 : " + content + "\n" + "수업 시간 : " + date +"\n"+ "신청 현황  : " + nowNum + "/" + maxNum
        
            btn1 = Button(self, text = strClass, padx =10 ,pady = 15)
            btn1.pack(padx  =10, pady =10)

        myPageBtn = Button(self, text="Go to the MyPage",
                           command=lambda: controller.show_frame("MyPage"))

        ManagerBtn = Button(self, text="Go to ManagerPage",
                           command=self.mng)
        logoutBtn = Button(self, text = "Logout",
                          command=lambda: controller.show_frame("LoginPage"))
        
        myPageBtn.pack()

        ManagerBtn.pack()
        logoutBtn.pack()

    
#---------------------------------------------------------

#-------------------- 관리자 페이지 --------------------
    ##mng : 관리자 로그인 페이지
    def mng(self):

        ###mngpw : 관리자 비밀번호
        self.mngpw="password"

        ###mngTL : 관리자 로그인 페이지
        self.mngTL = Toplevel(self)
        self.mngTL.title(MNGTITLE)
        self.mngTL.geometry("250x80")
        ####관리자 로그인 페이지 맨 앞으로
        self.mngTL.attributes("-topmost", True)

        Label(self.mngTL, text="관리자 비밀번호").place(x=30, y=10)

        ###mngpwSV : 입력한 관리자 비밀번호
        self.mngpwSV = StringVar("")
        ###mngpwE : 관리자 비밀번호 입력 Entry
        self.mngpwE = Entry(self.mngTL, show="*", textvariable=self.mngpwSV)
        self.mngpwE.place(x=30, y=40)
        ###trymnglog : 관리자 로그인 초기화
        self.trymnglog=-1
        self.mngpwE.bind("<Return>", self.bemng)

        ###mnglogB : 관리자 로그인 버튼
        mnglogB = Button(self.mngTL, text="입력", command=self.mnglog, width=5)
        mnglogB.place(x=190, y=35)

        self.mngTL.mainloop()

    ##bemng : 관리자 로그인 시도
    def bemng(self, event):
        ###관리자 로그인 시도 중
        self.trymnglog=0
        if(self.trymnglog==0):
            self.mnglog()
            ###trymnglog : 관리자 로그인 초기화
            self.trymnglog=-1

    ##mnglog : 관리자 로그인
    def mnglog(self):
        ###관리자 비밀번호와 입력한 관리자 비밀번호가 같으면 로그인 성공
        if(self.mngpw==str(self.mngpwSV.get())):
            ####관리자 로그인 페이지를 종료
            self.mngTL.destroy()
            ####tryadd : 수업/회원 등록 프레임 초기화
            self.tryadd=-1
            ####관리자 페이지 열기
            self.mngpg()
        ###로그인 실패
        else:
            ####실패 메세지박스 보이기
            messagebox.showinfo("information", "비밀번호가 틀렸습니다.")
            ####Entry에 입력한 내용 초기화
            self.mngpwE.delete(0,END)

    ##mngpg : 관리자 페이지
    def mngpg(self):
        ###mngpgTL : 관리자 페이지
        self.mngpgTL = Toplevel(self)
        self.mngpgTL.title(MNGTITLE)
        self.mngpgTL.geometry("250x150")
        ####관리자 페이지 맨 앞으로
        self.mngpgTL.attributes("-topmost", True)

        ###mb : 관리자 페이지 메뉴
        mb=Menu(self.mngpgTL)
        mb.add_command(label="수업등록", command=self.tryaddClass)
        mb.add_command(label="회원등록", command=self.tryaddMember)
        self.mngpgTL.config(menu=mb)
    
    ##tryaddClass : 수업 등록 프레임
    def tryaddClass(self):
        ###기존에 열려있는 프레임이 있으면 종료
        if(self.tryadd==0):
            self.addcF.destroy()
        elif(self.tryadd==1):
            self.addmF.destroy()

        #수업 등록 중
        self.tryadd=0
        #addcF : 수업 등록 프레임
        self.addcF = Frame(self.mngpgTL)
        self.addcF.grid(row=0, column=0)

        Label(self.addcF, text="수업 등록", padx=10, pady=5).grid(row=0, column=0)

        ###cName : 수업이름
        Label(self.addcF, text="이름").grid(row=1, column=0)
        self.cName = Entry(self.addcF)
        self.cName.grid(row=1, column=1)

        ###cDate : 수업날짜
        Label(self.addcF, text="날짜").grid(row=2, column=0)
        self.cDate = Entry(self.addcF)
        self.cDate.grid(row=2, column=1)

        ###mLimit : 수업인원
        Label(self.addcF, text="인원").grid(row=3, column=0)
        self.mLimit = Entry(self.addcF)
        self.mLimit.grid(row=3, column=1)

        ###addcB : 수업등록 버튼
        addcB = Button(self.addcF, text="등록", command=self.addClick, width=5)
        addcB.grid(row=4, column=1, sticky="E", pady=5)
        
    ##tryaddMember : 회원 등록 프레임
    def tryaddMember(self):
        ###기존에 열려있는 프레임이 있으면 종료
        if(self.tryadd==0):
            self.addcF.destroy()
        elif(self.tryadd==1):
            self.addmF.destroy()

        ###회원 등록 중
        self.tryadd=1
        ###addmF : 회원 등록 프레임
        self.addmF = Frame(self.mngpgTL)
        self.addmF.grid(row=0, column=1)
        
        Label(self.addmF, text="회원 등록", padx=10, pady=5).grid(row=0, column=0)

        ###mbNae : 회원이름
        Label(self.addmF, text="이름").grid(row=1, column=0)
        self.mbName = Entry(self.addmF)
        self.mbName.grid(row=1, column=1)

        ###mbNum : 회원번호
        Label(self.addmF, text="번호").grid(row=2, column=0)
        self.mbNum = Entry(self.addmF)
        self.mbNum.grid(row=2, column=1)

        ###rTime : 잔여횟수
        Label(self.addmF, text="횟수").grid(row=3, column=0)
        self.rTime = Entry(self.addmF)
        self.rTime.grid(row=3, column=1)

        ###addmB : 회원등록 버튼
        addmB = Button(self.addmF, text="등록", command=self.addClick, width=5)
        addmB.grid(row=4, column=1, sticky="E", pady=5)

    ##addClick : 등록 버튼 클릭
    def addClick(self):
        ###등록 질문 메세지박스
        if (messagebox.askokcancel("Redirecting", "등록하시겠습니까?")):
            ###확인 버튼 클릭 시 등록
            if (self.tryadd==0):
                self.addClass()
            elif (self.tryadd==1):
                self.addMember()

    ##addClass : 수업등록
    def addClass(self):
        print("수업등록:", str(self.cName.get()), str(self.cDate.get()), str(self.mLimit.get()))

    ##addMember : 회원등록
    def addMember(self):
        print("회원등록:", str(self.mbName.get()), str(self.mbNum.get()), str(self.rTime.get()))
#-------------------------------------------------------

#-------------------- 마이 페이지 --------------------
class MyPage(Frame):
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="This is MyPage 1")
        label.pack(side="top", fill="x", pady=10)
        reservationBtn = Button(self, text="Go back",
                           command=lambda: controller.show_frame("ReservationPage"))
        logoutBtn = Button(self, text = "Logout",
                          command=lambda: controller.show_frame("LoginPage"))
        
        reservationBtn.pack()
        logoutBtn.pack()
#-----------------------------------------------------

'''
class ManagerPage(Frame):
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="This is MagerPage 1")
        label.pack(side="top", fill="x", pady=10)
        myPageBtn = Button(self, text="Go to the MyPage",
                           command=lambda: controller.show_frame("MyPage"))
        reservationBtn = Button(self, text="Go back",
                           command=lambda: controller.show_frame("ReservationPage"))
        logoutBtn = Button(self, text = "Logout",
                          command=lambda: controller.show_frame("LoginPage"))
        
        myPageBtn.pack()
        reservationBtn.pack()
        ManagerBtn.pack()
        logoutBtn.pack()
'''

#-------------------- 로그인 페이지 --------------------
class LoginPage(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # 회원번호를 입력해 달라는 Label
        Label(self, text="회원번호를 입력해주세요").grid(row=0, padx=10, pady=10)

        # 회원번호 입력 Entry
        logID = Entry(self)
        logID.grid(row=1, padx=10, pady=10)

        # 로그인 Button
        btnLogin = Button(self, text="로그인",
                            command=lambda: controller.show_frame("ReservationPage"))
        btnLogin.grid(row=2, padx=10, pady=10)
#-------------------------------------------------------        

        
if __name__ == "__main__":
    app = MainClass()
    app.mainloop()
