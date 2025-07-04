package com.liqun.aigc_adgraph_front.ui.screens

import android.util.Log
import androidx.compose.animation.core.*
import androidx.compose.animation.rememberSplineBasedDecay
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.FlingBehavior
import androidx.compose.foundation.gestures.Orientation
import androidx.compose.foundation.gestures.ScrollScope
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.draggable
import androidx.compose.foundation.gestures.rememberDraggableState
import androidx.compose.foundation.gestures.rememberScrollableState
import androidx.compose.foundation.gestures.scrollable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.PagerDefaults
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.rounded.Favorite
import androidx.compose.material.icons.rounded.Share
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.zIndex
import com.liqun.aigc_adgraph_front.model.NovelData
import com.liqun.aigc_adgraph_front.ui.theme.*
import kotlinx.coroutines.launch
import kotlin.math.absoluteValue
import kotlin.math.min
import kotlin.math.roundToInt
import kotlin.math.sign

@OptIn(ExperimentalFoundationApi::class, ExperimentalMaterial3Api::class)
@Composable
fun PreviewScreen(modifier: Modifier = Modifier, onBack: () -> Unit) {
    var showDeployDialog by remember { mutableStateOf(false) }
    
    // 获取屏幕宽度以计算卡片位置
    val configuration = LocalConfiguration.current
    val screenWidth = configuration.screenWidthDp.dp
    val density = LocalDensity.current
    val pixelDensity = density.density
    
    // 添加协程作用域
    val coroutineScope = rememberCoroutineScope()
    
    // 使用索引跟踪当前卡片
    var currentIndex by remember { mutableStateOf(0) }
    
    // 简化状态管理 - 使用单一偏移量控制滑动
    // 这样可以减少每帧的计算量，提高流畅度
    var offsetX by remember { mutableStateOf(0f) }
    
    // 卡片间距
    val cardSpacing = 320f
    val cardCount = NovelData.paragraphs.size
    
    // 获取Context，用于资源访问
    val context = LocalContext.current
    
    // 获取段落对应的图片资源ID
    fun getDrawableResourceId(index: Int): Int {
        val resourceName = NovelData.getParagraphImageName(index)
        return context.resources.getIdentifier(resourceName, "drawable", context.packageName)
    }
    
    // 共享滑动状态 - 允许在任何区域滑动
    val scrollableState = rememberScrollableState { delta ->
        // 添加边界限制，确保不能滑出第一张或最后一张卡片
        val minOffset = -(cardCount - 1) * cardSpacing  // 最小偏移量（最后一张卡片）
        val maxOffset = 0f  // 最大偏移量（第一张卡片）
        
        // 计算新的偏移量，添加阻尼效果
        val newOffset = when {
            // 已经是第一张卡片且继续向右滑动 (delta > 0)
            offsetX >= maxOffset && delta > 0 -> {
                // 添加阻尼效果，实际移动距离减小到原来的20%
                offsetX + delta * 0.2f
            }
            // 已经是最后一张卡片且继续向左滑动 (delta < 0)
            offsetX <= minOffset && delta < 0 -> {
                // 添加阻尼效果，实际移动距离减小到原来的20%
                offsetX + delta * 0.2f
            }
            // 正常范围内，完全响应滑动
            else -> {
                (offsetX + delta).coerceIn(minOffset, maxOffset)
            }
        }
        
        // 计算实际消耗的delta
        val consumed = newOffset - offsetX
        
        // 更新偏移量
        offsetX = newOffset
        
        // 返回实际消耗的滑动量
        consumed
    }
    
    // 自定义惯性参数
    val flingBehavior = remember {
        object : FlingBehavior {
            override suspend fun ScrollScope.performFling(initialVelocity: Float): Float {
                // 添加边界限制
                val minOffset = -(cardCount - 1) * cardSpacing
                val maxOffset = 0f
                
                // 计算最终目标位置
                val targetPosition = when {
                    initialVelocity > 1000f -> offsetX + cardSpacing  // 向左快速滑动
                    initialVelocity < -1000f -> offsetX - cardSpacing  // 向右快速滑动
                    else -> {
                        // 否则滚动到最近的卡片位置
                        val cardPosition = (offsetX / cardSpacing).roundToInt() * cardSpacing
                        val distanceToCard = offsetX - cardPosition
                        
                        if (distanceToCard.absoluteValue > cardSpacing * 0.5f) {
                            // 如果超过一半距离，滚到下一个/上一个卡片
                            cardPosition + cardSpacing * distanceToCard.sign
                        } else {
                            // 否则回到最近的卡片
                            cardPosition
                        }
                    }
                }.coerceIn(minOffset, maxOffset)  // 确保目标位置在有效范围内
                
                // 计算新索引 - 修复计算方式确保正确定位
                val calculatedIndex = (-(targetPosition / cardSpacing).roundToInt())
                    .coerceIn(0, cardCount - 1)
                
                // 启动平滑动画，修正目标位置确保卡片停在正确位置
                animate(
                    initialValue = offsetX,
                    targetValue = -calculatedIndex * cardSpacing,
                    initialVelocity = initialVelocity / 3,
                    animationSpec = spring(
                        dampingRatio = 0.8f,
                        stiffness = 400f
                    )
                ) { value, _ ->
                    offsetX = value
                }
                
                // 更新当前索引
                currentIndex = calculatedIndex
                
                return 0f // 消耗所有速度
            }
        }
    }
    
    Box(modifier = modifier.fillMaxSize()) {
        // iOS风格的背景 - 使用主题颜色
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            BlackAlpha60,
                            Color(0xCC000000)
                        )
                    )
                )
        )
        
        // 顶部栏 - 使用更醒目的设计确保返回按钮可见
        CenterAlignedTopAppBar(
            title = { 
                Text(
                    "预览画面", 
                    color = Color.White,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.SemiBold
                ) 
            },
            navigationIcon = {
                FilledTonalIconButton(
                    onClick = { 
                        println("返回按钮被点击")
                        onBack() 
                    },
                    modifier = Modifier.size(48.dp),
                    colors = IconButtonDefaults.filledTonalIconButtonColors(
                        containerColor = Color.White.copy(alpha = 0.2f),
                        contentColor = Color.White
                    )
                ) {
                    Icon(
                        imageVector = Icons.Filled.ArrowBack, 
                        contentDescription = "返回",
                        tint = Color.White
                    )
                }
            },
            colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                containerColor = Color.Transparent,
                titleContentColor = Color.White
            )
        )
        
        // 卡片区域 - 简化的滑动实现
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(top = 56.dp, bottom = 80.dp),
            contentAlignment = Alignment.Center
        ) {
            // 优化的滑动区域 - 使用更基础的手势处理
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .scrollable(
                        orientation = Orientation.Horizontal,
                        state = scrollableState,
                        flingBehavior = flingBehavior
                    )
            )
            
            // 添加卡片指示器
            Row(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 8.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                repeat(cardCount) { index ->
                    val isActive = index == currentIndex
                    Box(
                        modifier = Modifier
                            .padding(horizontal = 4.dp)
                            .size(if (isActive) 10.dp else 8.dp)
                            .background(
                                color = if (isActive) MaterialTheme.colorScheme.primary else Color.White.copy(alpha = 0.5f),
                                shape = RoundedCornerShape(50)
                            )
                    )
                }
            }
            
            // 3D卡片展示 - 保留原有功能并优化
            for (i in 0 until cardCount) {
                // 计算每张卡片的偏移量 - 基于主偏移量
                val cardOffsetX = offsetX + i * cardSpacing
                
                // 只渲染可见范围内的卡片 (±2卡片距离)
                if (cardOffsetX.absoluteValue < screenWidth.value * 1.5f) {
                    val absOffset = cardOffsetX.absoluteValue
                    
                    // 缩放和透明度 - 使当前卡片更突出
                    val scale = 0.8f + 0.2f * (1f - min(1f, absOffset / 320f))
                    val alpha = if (absOffset < 350f) 1f else (1f - (absOffset - 350f) / 350f).coerceIn(0.3f, 1f)
                    
                    // Z轴层叠顺序 - 更简单的计算方式
                    val zIndex = 10f - (absOffset / 50f).coerceAtMost(9f)
                    
                    // Y轴位移 - 创建堆叠效果
                    val yOffset = min(absOffset * 0.1f, 40f)

                    // 添加阴影效果，使3D效果更明显
                    val elevation = if (absOffset < 50f) 16.dp else 8.dp
                    
                    // iOS风格的卡片
                    Box(
                        modifier = Modifier
                            .offset {
                                IntOffset(
                                    x = cardOffsetX.roundToInt(),
                                    y = yOffset.roundToInt()
                                )
                            }
                            .zIndex(zIndex)
                            .graphicsLayer {
                                this.scaleX = scale
                                this.scaleY = scale
                                this.alpha = alpha
                                // 旋转角度 - 比例更小避免过度旋转
                                this.rotationY = (cardOffsetX / 500f) * 8f
                                this.cameraDistance = 8f * pixelDensity
                            }
                    ) {
                        // 卡片内容 - 添加滑动手势和更好的视觉效果
                        Card(
                            modifier = Modifier
                                .width(300.dp)
                                .height(500.dp)
                                .shadow(
                                    elevation = elevation,
                                    shape = CardShape,
                                    spotColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.5f)
                                )
                                // 添加滑动功能到卡片本身
                                .scrollable(
                                    orientation = Orientation.Horizontal,
                                    state = scrollableState,
                                    flingBehavior = flingBehavior
                                ),
                            shape = CardShape,
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surface
                            ),
                            elevation = CardDefaults.cardElevation(defaultElevation = elevation)
                        ) {
                            // 卡片内容布局
                            Column(
                                modifier = Modifier.fillMaxSize()
                            ) {
                                // 图片区域
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .weight(0.7f)
                                        .background(
                                            brush = Brush.verticalGradient(
                                                colors = listOf(
                                                    CardGradientStart,
                                                    CardGradientEnd
                                                )
                                            )
                                        ),
                                    contentAlignment = Alignment.Center
                                ) {
                                    // 获取图片资源ID
                                    val drawableId = getDrawableResourceId(i)
                                    
                                    if (drawableId != 0) {
                                        // 如果找到资源，显示图片
                                        Image(
                                            painter = painterResource(id = drawableId),
                                            contentDescription = NovelData.getParagraphImageDescription(i),
                                            modifier = Modifier.fillMaxSize(),
                                            contentScale = ContentScale.Crop
                                        )
                                    } else {
                                        // 如果未找到资源，显示默认内容
                                        Text(
                                            text = "图片 ${i + 1} (尚未生成)",
                                            style = MaterialTheme.typography.headlineMedium,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant
                                        )
                                    }
                                }
                                
                                // 文本区域
                                Column(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .weight(0.3f)
                                        .padding(16.dp)
                                ) {
                                    Text(
                                        text = NovelData.paragraphs[i],
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onSurface,
                                        maxLines = 5,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                    
                                    Spacer(modifier = Modifier.weight(1f))
                                }
                            }
                        }
                    }
                }
            }
        }

        // 底部发布按钮
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp, vertical = 24.dp)
                .align(Alignment.BottomCenter),
            contentAlignment = Alignment.Center
        ) {
            Button(
                onClick = { showDeployDialog = true },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                shape = ButtonShape,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    contentColor = Color.White
                ),
                elevation = ButtonDefaults.buttonElevation(
                    defaultElevation = 4.dp,
                    pressedElevation = 8.dp
                )
            ) {
                Text(
                    "一键发布到社交平台",
                    style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
                )
            }
        }
    }

    // iOS风格对话框
    if (showDeployDialog) {
        AlertDialog(
            onDismissRequest = { showDeployDialog = false },
            modifier = Modifier.clip(DialogShape),
            title = { 
                Text(
                    "确认发布",
                    style = MaterialTheme.typography.headlineSmall
                ) 
            },
            text = { 
                Text(
                    "确定要将当前生成的图片发布到社交媒体吗？",
                    style = MaterialTheme.typography.bodyLarge
                ) 
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        // TODO: 实现部署逻辑
                        showDeployDialog = false
                    }
                ) {
                    Text(
                        "确定",
                        color = MaterialTheme.colorScheme.primary,
                        style = MaterialTheme.typography.labelLarge
                    )
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeployDialog = false }) {
                    Text(
                        "取消",
                        style = MaterialTheme.typography.labelLarge
                    )
                }
            }
        )
    }
    
    // 添加惯性边界矫正效果
    LaunchedEffect(offsetX) {
        // 设置有效边界
        val minOffset = -(cardCount - 1) * cardSpacing
        val maxOffset = 0f
        
        // 当偏移量超出边界时，添加自动回弹
        if (offsetX > maxOffset || offsetX < minOffset) {
            // 计算目标位置
            val targetOffset = offsetX.coerceIn(minOffset, maxOffset)
            
            // 使用动画平滑过渡回有效范围
            animate(
                initialValue = offsetX,
                targetValue = targetOffset,
                animationSpec = spring(
                    dampingRatio = 0.7f,
                    stiffness = 300f
                )
            ) { value, _ ->
                offsetX = value
            }
        }
        
        // 更新当前索引
        val calculatedIndex = (-(offsetX / cardSpacing).roundToInt())
            .coerceIn(0, cardCount - 1)
        
        // 只有当计算出的索引与当前索引不同时才更新
        if (calculatedIndex != currentIndex) {
            currentIndex = calculatedIndex
            println("切换到卡片: $currentIndex, 偏移量: $offsetX")
        }
    }
    
    // 增强监听逻辑，确保返回键和其他交互正常工作
    LaunchedEffect(onBack) {
        println("预览界面初始化完成，返回按钮已配置")
    }
    
    // 初始设置
    LaunchedEffect(Unit) {
        // 初始化偏移量以显示第一张卡片
        offsetX = 0f
        currentIndex = 0
        
        // 打印日志帮助调试
        println("初始化预览界面，卡片数量: $cardCount")
    }
}