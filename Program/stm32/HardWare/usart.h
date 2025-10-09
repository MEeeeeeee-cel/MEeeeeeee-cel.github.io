#ifndef __USART_H
#define __USART_H
#include "stdio.h"	
#include "stdint.h"
extern uint8_t Serial_RxPaket[];
extern uint8_t Serial_RxFlag;
void Serial_Init(void);
void Serial_SendByte(uint8_t Byte);
void Serial_printf(char *fomat,...);
void Serial_SendArray(uint8_t *Array,uint16_t Length);
uint16_t Serial_Ro(uint8_t Hight,uint8_t Low);
#endif


