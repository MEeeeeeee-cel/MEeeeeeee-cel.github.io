#include "stm32f10x.h"                  // Device header
uint16_t DMAsize;
void DMA_INIT(uint32_t MemoryAddr,uint32_t PeripheralAddr, uint32_t times)
{
	DMAsize=times;
	RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1,ENABLE);
	DMA_InitTypeDef  DMA_InitStructure;
	DMA_InitStructure.DMA_MemoryBaseAddr=MemoryAddr;
	DMA_InitStructure.DMA_MemoryDataSize=DMA_MemoryDataSize_Byte ;
	DMA_InitStructure.DMA_MemoryInc=DMA_MemoryInc_Enable;
	DMA_InitStructure.DMA_PeripheralBaseAddr=PeripheralAddr;
	DMA_InitStructure.DMA_PeripheralDataSize=DMA_PeripheralDataSize_Byte;
	DMA_InitStructure.DMA_PeripheralInc=DMA_PeripheralInc_Enable;
	DMA_InitStructure.DMA_BufferSize=times;									//传输器数值
	DMA_InitStructure.DMA_DIR=DMA_DIR_PeripheralSRC;						//传输方向
	DMA_InitStructure.DMA_M2M=DMA_M2M_Enable;								//硬件软件触发
	DMA_InitStructure.DMA_Mode=DMA_Mode_Normal;								//是否自动重装值
	
	DMA_InitStructure.DMA_Priority=DMA_Priority_Medium ;
		
	DMA_Init(DMA1_Channel1,&DMA_InitStructure);
	
	DMA_Cmd(DMA1_Channel1,DISABLE);
	
}

void DMA_Tranf(void)
{
	DMA_Cmd(DMA1_Channel1,DISABLE);
	DMA_SetCurrDataCounter(DMA1_Channel1,DMAsize);
	DMA_Cmd(DMA1_Channel1,ENABLE);
	while(DMA_GetFlagStatus(DMA1_FLAG_TC1)==RESET);
	DMA_ClearFlag(DMA1_FLAG_TC1);
}


