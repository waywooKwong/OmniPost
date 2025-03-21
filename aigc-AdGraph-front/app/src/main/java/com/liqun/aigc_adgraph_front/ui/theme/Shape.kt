package com.liqun.aigc_adgraph_front.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.compose.ui.unit.dp

// 定义应用程序中使用的自定义形状
val Shapes = Shapes(
    // 小尺寸组件（按钮、小卡片等）的形状
    small = RoundedCornerShape(8.dp),
    
    // 中等尺寸组件（卡片、对话框等）的形状
    medium = RoundedCornerShape(12.dp),
    
    // 大尺寸组件（底部表单、模态框等）的形状
    large = RoundedCornerShape(16.dp),
    
    // 额外大尺寸（全屏卡片、底部表单等）的形状
    extraLarge = RoundedCornerShape(24.dp)
)

// iOS风格的形状常量，可在需要时使用
val CircleShape = RoundedCornerShape(percent = 50)
val CardShape = RoundedCornerShape(16.dp)
val ButtonShape = RoundedCornerShape(24.dp)
val BottomSheetShape = RoundedCornerShape(
    topStart = 24.dp,
    topEnd = 24.dp,
    bottomStart = 0.dp,
    bottomEnd = 0.dp
)
val DialogShape = RoundedCornerShape(28.dp) 