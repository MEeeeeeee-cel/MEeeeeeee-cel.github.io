#include "stm32f10x.h"                  // Device header
#include "DS18B20.h"
#include "OLED.h"
#include "Delay.h"
#include "stdio.h"

void DS18B20_RST(void)
{
	DS18B20_IO_OUT();
	DS18B20_DQ_OUT=0;
	Delay_us(750);
	DS18B20_DQ_OUT=1;
	Delay_us(15);
}

uint8_t DS18B20_CHECK(void)
{
	DS18B20_IO_IN(); //设置成输入模式
	uint16_t delay_cnt=0;
	//如果信号线在200us内未被拉低，则应答失败
	while((DS18B20_DQ_IN) && (delay_cnt<200))
	{
		delay_cnt++;
		Delay_us(1);
	}
	if(delay_cnt>=200)
	{
		OLED_ShowNum(3,1,1,2);
		return 1;
	}
	else
	{
		delay_cnt = 0;
	}
	//如果信号线超过240us未被拉高，则应答失败
	while((!DS18B20_DQ_IN) && (delay_cnt<240))
	{
		delay_cnt++;
		Delay_us(1);
	}
	if(delay_cnt>=240)
	{
		OLED_ShowNum(3,1,2,2);
		return 1;
	}
	else
	{
		delay_cnt=0;
	}
	return 0;
}

uint8_t DS18B20_READ_BIT(void)
{
  uint8_t bit;
	DS18B20_IO_OUT();
  DS18B20_DQ_OUT=0;
	Delay_us(2);
  DS18B20_DQ_OUT=1;
	DS18B20_IO_IN();
	Delay_us(12);
	if(DS18B20_DQ_IN)
		bit=1;
  else
		bit=0;	 
  Delay_us(50);           
	return bit;
}

uint8_t DS18B20_READ_BYTE(void)
{
  uint8_t i,bit,byte;
  byte=0;
	for (i=1;i<=8;i++) 
	{
		bit=DS18B20_READ_BIT();
		byte=(bit<<7)|(byte>>1);
  }
  return byte;
}

void DS18B20_WRITE_BYTE(uint8_t byte)
{
	uint8_t j;
  uint8_t testb;
	DS18B20_IO_OUT();
  for (j=1;j<=8;j++) 
	{
    testb=byte & 0x01;
    byte=byte >> 1;
    if (testb)
    {
			DS18B20_DQ_OUT=0;
      Delay_us(2);
      DS18B20_DQ_OUT=1;
      Delay_us(60);
    }
    else
    {
      DS18B20_DQ_OUT=0;
      Delay_us(60);
      DS18B20_DQ_OUT=1;
      Delay_us(2);
    }
  }
}

void DS18B20_START(void)
{
  DS18B20_RST();
	DS18B20_CHECK();
  DS18B20_WRITE_BYTE(0xcc);
  DS18B20_WRITE_BYTE(0x44);
} 
 	 
uint8_t DS18B20_INIT(void)
{
 	GPIO_InitTypeDef  GPIO_InitStructure;
 	RCC_APB2PeriphClockCmd(DS18B20_GPIO_CLK, ENABLE);
 	GPIO_InitStructure.GPIO_Pin = DS18B20_GPIO_PIN;
 	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
 	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
 	GPIO_Init(DS18B20_GPIO_PORT, &GPIO_InitStructure);
	
 	GPIO_SetBits(DS18B20_GPIO_PORT,DS18B20_GPIO_PIN);
	
	DS18B20_RST();
	return DS18B20_CHECK();
}  

int16_t DS18B20_GET_TEMPERATURE(void)
{
  uint8_t data_flag;
  uint8_t data_l,data_h;
	uint16_t temp;
  DS18B20_START();
	Delay_ms(20);
  DS18B20_RST();
  DS18B20_CHECK();
  DS18B20_WRITE_BYTE(0xcc);
  DS18B20_WRITE_BYTE(0xbe);
  data_l=DS18B20_READ_BYTE(); //获取低八位
  data_h=DS18B20_READ_BYTE(); //获取高八位
  if(data_h>7) //判断是不是负数
  {
    data_h = ~data_h;
    data_l = ~data_l+1;
    data_flag = 0;
  }
	else
		data_flag = 1;
  temp = data_h;
  temp = temp<<8;
  temp = temp + data_l;
  temp = (float)temp*0.0625;
	if(data_flag)
		return temp;
	else
		return -temp;
}
