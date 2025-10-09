#include<reg51.h>           //预处理命令，定义SFR的头文件
#include <math.h>           //数学函数库文件
#define uchar unsigned char //定义无符号字符变量uchar
#define uint  unsigned int  //定义无符号整型变量uint
#define lcd_data P0         //定义LCD1602接口P0

sbit DQ=P1^7;               //将DQ位定义为P1.7引脚
sbit lcd_RS=P2^0;           //将RS位定义为P2.0引脚
sbit lcd_RW=P2^1;           //将RW位定义为P2.1引脚
sbit lcd_EN=P2^2;           //将EN位定义为P2.2引脚
sbit PWM=P3^7;              //将PWM定义为P3.7引脚
sbit D=P3^6;                //将D定义为P3.6引脚，转向选择位

uchar t[2], speed, temperature; //用来存放温度值
uchar DS18B20_is_ok;
uchar TempBuffer1[12]={0x20, 0x20, 0x20, 0x20, 0xdf, 0x43, '\0'};
uchar tab[16]={0x20,0x20,0x20,0x54,0x20,0x4d,0x6f,0x6e,0x69,0x74,0x6f,0x72, '\0'};

/***********lcd显示子程序***********/
void delay_20ms(void)       /*延时20ms函数*/
{
    uchar i, temp;          //声明变量i，temp
    for(i = 20; i > 0; i--) //循环
    {
        temp = 248;         //给temp赋值248
        while(--temp);      //temp减1是否等于0，否则继续执行该行
        temp = 248;         //给temp赋值248
        while(--temp);      //temp减1是否等于0，否则继续执行该行
    }
}

void delay_38us(void)       /*延时38μs函数*/
{
    uchar temp;             //声明变量temp
    temp = 18;              //给temp赋值
    while(--temp);          //temp减1是否等于0，否则继续执行该行
}

void delay_1520us(void)     /*延时1520μs函数*/
{
    uchar i, temp;          //声明变量i，temp
    for(i = 3; i > 0; i--)  //循环
    {
        temp = 252;         //给temp赋值
        while(--temp);      //temp减1是否等于0，否则继续执行该行
    }
}

uchar lcd_rd_status()       /*读取lcd1602的状态，主要用于判断是否忙*/
{
    uchar tmp_sts;          //声明变量tmp_sts
    lcd_data = 0xff;        //初始化P3口
    lcd_RW = 1;             //RW =1 读
    lcd_RS = 0;             //RS =0 命令，合起来表示读命令(状态)
    lcd_EN = 1;
    //EN=1，打开EN，lcd1602开始输出命令数据，100ns之后命令数据有效
    tmp_sts = lcd_data;     //读取命令到tmp_sts
    lcd_EN = 0;             //关掉lcd1602
    lcd_RW = 0;             //把lcd1602设置成写
    return tmp_sts;         //函数返回值tmp_sts
}

void lcd_wr_com(uchar command) /*写一个命令到lcd1602*/
{
    while(0x80 & lcd_rd_status());
    //写之前先判断LCD1602是否忙，看读出的命令的最高位是否为1，为1表示忙，继续读，直到不忙
    lcd_RW = 0;
    lcd_RS = 0;             //RW=0，RS=0 写命令
    lcd_data = command;     //把需要写的命令写到数据线上
    lcd_EN = 1;
    lcd_EN = 0;             //EN输出高电平脉冲，命令写入
}

void lcd_wr_data(uchar sjdata) /*写一个显示数据到lcd1602*/
{
    while(0x80 & lcd_rd_status());
    //写之前先判断lcd1602是否忙，看读出的命令的最高位是否为1，为1表示忙，继续读，直到不忙
    lcd_RW = 0;
    lcd_RS = 1;             //RW=0，RS=1 写显示数据
    lcd_data = sjdata;      //把需要写的显示数据写到数据线上
    lcd_EN = 1;
    lcd_EN = 0;             //EN输出高电平脉冲，命令写入
    lcd_RS = 0;
}

void Init_lcd(void)          /*初始化lcd1602*/
{
    delay_20ms();           //调用延时
    lcd_wr_com(0x38);       //设置16*2格式，5*8点阵，8位数据接口
    delay_38us();           //调用延时
    lcd_wr_com(0x0c);       //开显示，不显示光标
    delay_38us();           //调用延时
    lcd_wr_com(0x01);       //清屏
    delay_1520us();         //调用延时
    lcd_wr_com(0x06);       //显示一个数据后光标自动+1
}

void GotoXY(uchar x, uchar y) //设定位置，x为列，y为行
{
    if(y == 0)              //如果y=0，则显示位置为第一行
        lcd_wr_com(0x80 | x);
    if(y == 1)              //如果y=1，则显示位置为第二行
        lcd_wr_com(0xc0 | x);
}

void Print(uchar *str)       //显示字符串函数
{
    while(*str != '\0')     //判断字符串是否显示完
    {
        lcd_wr_data(*str);  //写数据
        str++;
    }
}

void LCD_Print(uchar x, uchar y, uchar *str)
//x为行值，y为列值，str是要显示的字符串
{
    GotoXY(x, y);           //设定显示位置
    Print(str);             //显示字符串
}

/******************系统显示子函数******************/
void covert1() {
    int temp;
    uchar sign = '+';
    
    temp = (int)(t[1] << 8) | t[0];//源码的正负号和补码判断是错误的
    
    if(temp & 0x8000) {
        sign = '-';
        temp = (~temp + 1) & 0xFFFF;
    }
    
    temperature = temp >> 4;
    
    if(temperature < -55) temperature = -55;
    if(temperature > 125) temperature = 125;//限幅
    
    TempBuffer1[0] = sign;
    
    if(abs(temperature) >= 100) {
        TempBuffer1[1] = abs(temperature)/100 + '0';
    } else {
        TempBuffer1[1] = ' ';
    }
    
    TempBuffer1[2] = (abs(temperature)%100)/10 + '0';
    
    TempBuffer1[3] = abs(temperature)%10 + '0';
    
    TempBuffer1[4] = 0xDF;
    TempBuffer1[5] = 'C';
    TempBuffer1[6] = '\0';
}


/******************DS18B20函数******************/
void delay_18B20(uint i)     //延时程序
{
    while(i--);
}

uchar Init_DS18B20(void)      //DS18B20初始化函数
{
    uchar x = 0;
    DQ = 1;                  //DQ复位
    delay_18B20(8);          //稍做延时
    DQ = 0;                  //单片机将DQ拉低
    delay_18B20(80);         //精确延时大于480μs
    DQ = 1;                  //拉高总线
    delay_18B20(14);
    x = DQ;                  //稍做延时后，如果x=0则初始化成功；如果x=1则初始化失败
    delay_18B20(20);
		return x;
}




uchar ReadOneChar(void)      //DS18B20读一个字节函数
{
    unsigned char i = 0;
    unsigned char dat0 = 0;
    for (i = 8; i > 0; i--)
    {
        DQ = 0;              //读前总线保持为低
        dat0 >>= 1;						//移位存储新数据
        DQ = 1;              //开始读总线释放
        if(DQ)               //从DS18B20总线读得一位
            dat0 |= 0x80;
        delay_18B20(4);      //延时一段时间
    }
    return(dat0);            //返回数据
}



void WriteOneChar(uchar dat1) //DS18B20写一个字节函数
{
    uchar i = 0;
    for (i = 8; i > 0; i--)
    {
        DQ = 0;              //开始写入DS18B20总线要处于复位(低)状态
        DQ = dat1 & 0x01;    //写入下一位
        delay_18B20(5);
        DQ = 1;              //重新释放总线
        dat1 >>= 1;          //把一个字节分成8个BIT环移给DQ
    }
}

void ReadTemperature()       //读取DS18B20当前温度
{
    delay_18B20(80);         //延时一段时间
    Init_DS18B20();
    WriteOneChar(0xCC);      //跳过读序号列号的操作1100 1100
    WriteOneChar(0x44);      //启动温度转换
    delay_18B20(80);         //延时一段时间
    Init_DS18B20();          //DS18B20初始化
    WriteOneChar(0xCC);      //跳过读序号列号的操作
    WriteOneChar(0xBE);
    //读取温度寄存器等(共可读9个寄存器)，前两个就是温度
    delay_18B20(80);         //延时一段时间
    t[0] = ReadOneChar();    //读取温度值低位
    t[1] = ReadOneChar();    //读取温度值高位
}

/******************电机控制函数******************/
void delay_motor(uchar i)    //延时函数
{
    uchar j, k;              //变量i、k为无符号字符数据类型
    for(j = i; j > 0; j--)   //循环延时
        for(k = 200; k > 0; k--); //循环延时
}

void motor(uchar tmp)        //电机转动程序
{
    uchar x;
    if(TempBuffer1[0] == 0x2b) //温度为正数
    {
        if(tmp < 25)         //温度小于25℃
        {
            D = 0;           //电动机停止转动
            PWM = 0;
        }
        else if(tmp > 50)    //温度大于50℃，全速转动
        {
            D = 0;           //D置0
            PWM = 1;         //正转，PWM=1
            x = 250;         //时间常数为x
            delay_motor(x);  //调延时函数
            PWM = 0;
            x = 5;           //时间常数为x
            delay_motor(x);  //调延时函数
        }
        else
        {
            D = 0;           //D置0
            PWM = 1;         //正转，PWM=1
            x = 5 * tmp;     //时间常数为x
            delay_motor(x);  //调延时函数
            PWM = 0;
            x = 255 - 5 * tmp; //时间常数为255-x
            delay_motor(x);  //调延时函数
        }
    }
    else if (TempBuffer1[0] == 0x2d) //温度小于0，反转
    {
        D = 1;
        PWM = 0;
        x = 5 * tmp;         //时间常数为tmp
        delay_motor(x);      //调延时函数
        PWM = 1;
        x = 255 - 5 * tmp;   //时间常数为255-tmp
        delay_motor(x);      //调延时函数
    }
}




/******************通用延时函数******************/
void delay(unsigned int x)   //延时函数
{
    unsigned char i;         //定义变量i的类型
    while(x--)               //x自减1
    {
        for(i = 0; i < 123; i++); //控制延时的循环
    }
}

/***********************main主程序***********************/
void main(void)
{
    delay_20ms();            //系统延时20ms启动
    ReadTemperature();       //启动DS18B20
    Init_lcd();              //调用LCD初始化函数
    LCD_Print(0, 0, tab);    //液晶初始显示
    delay(1000);             //延时一段时间
    
    while(1)
    {
        ReadTemperature();   //读取温度，温度值存放在一个两个字节的数组中
        delay_18B20(100);
        covert1();           //数据转化
        LCD_Print(4, 1, TempBuffer1); //显示温度
        motor(temperature);  //电动机转动
    }
}
    



