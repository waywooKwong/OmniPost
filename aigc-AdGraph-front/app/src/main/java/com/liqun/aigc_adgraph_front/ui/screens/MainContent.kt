package com.liqun.aigc_adgraph_front.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close

import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Info
import androidx.compose.material.icons.rounded.MoreVert
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.liqun.aigc_adgraph_front.model.NovelData
import com.liqun.aigc_adgraph_front.ui.theme.*
import kotlinx.coroutines.delay

@Composable
fun MainContent(
    modifier: Modifier = Modifier,
    onPreview: () -> Unit
) {
    var isProcessing by remember { mutableStateOf(false) }
    var currentParagraphIndex by remember { mutableStateOf(0) }
    var isPaused by remember { mutableStateOf(false) }
    var showPreview by remember { mutableStateOf(false) }
    var showProgress by remember { mutableStateOf(false) }
    
    // 添加自动轮换效果
    LaunchedEffect(isProcessing, isPaused) {
        while (isProcessing && !isPaused && currentParagraphIndex < NovelData.paragraphs.size) {
            delay(2000) // 每2秒切换一次段落
            if (!isPaused) {
                currentParagraphIndex = (currentParagraphIndex + 1) % NovelData.paragraphs.size
            }
        }
    }
    
    // 存储生成的图片
    var generatedImages by remember { mutableStateOf(List(NovelData.paragraphs.size) { "" }) }
    var selectedParagraphIndex by remember { mutableStateOf(-1) }
    
    Box(modifier = modifier.fillMaxSize()) {
        if (!isProcessing) {
            // 显示欢迎界面
            WelcomeSection(
                modifier = Modifier.align(Alignment.Center),
                onUpload = { isProcessing = true }
            )
        } else {
            // 小说处理界面
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {
                // 进度指示器
                LinearProgressIndicator(
                    progress = { currentParagraphIndex.toFloat() / NovelData.paragraphs.size },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    color = MaterialTheme.colorScheme.primary,
                    trackColor = MaterialTheme.colorScheme.surfaceVariant
                )
                
                // 状态信息
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "处理中: ${currentParagraphIndex + 1}/${NovelData.paragraphs.size}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // 显示段落列表
                val listState = rememberLazyListState()
                
                LazyColumn(
                    state = listState,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth()
                ) {
                    items(NovelData.paragraphs) { paragraph ->
                        val isCurrentParagraph = NovelData.paragraphs.indexOf(paragraph) == currentParagraphIndex
                        val isSelected = NovelData.paragraphs.indexOf(paragraph) == selectedParagraphIndex
                        val paragraphIndex = NovelData.paragraphs.indexOf(paragraph)
                        
                        ParagraphCard(
                            text = paragraph,
                            isActive = isCurrentParagraph,
                            isSelected = isSelected,
                            onClick = {
                                if (!isCurrentParagraph) {
                                    selectedParagraphIndex = paragraphIndex
                                    showProgress = true
                                }
                            },
                            modifier = Modifier.padding(vertical = 6.dp)
                        )
                    }
                }
                
                // 活动段落预览 - 根据处理状态显示
                if (isProcessing && currentParagraphIndex < NovelData.paragraphs.size) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp)
                    ) {
                        // 显示当前段落的预览 - 无论是否暂停都显示
                        ActiveParagraphPreview(
                            index = currentParagraphIndex,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(180.dp)
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        // 底部控制按钮区域 - 始终显示
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            // 暂停/继续按钮
                            Button(
                                onClick = { isPaused = !isPaused },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = MaterialTheme.colorScheme.secondary
                                )
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = if (isPaused) Icons.Rounded.PlayArrow else Icons.Rounded.Close,
                                        contentDescription = if (isPaused) "继续" else "暂停"
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(if (isPaused) "继续" else "暂停")
                                }
                            }
                            
                            // 结束按钮
                            Button(
                                onClick = onPreview,
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = MaterialTheme.colorScheme.primary
                                )
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        imageVector = Icons.Filled.Close,
                                        contentDescription = "完成"
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("结束")
                                }
                            }
                        }
                    }
                }
            }
            
            // 生成进度弹窗 - 只对未完成的段落显示
            if (showProgress) {
                // 判断是否已经生成过
                val hasGeneratedImage = selectedParagraphIndex <= currentParagraphIndex
                
                if (hasGeneratedImage) {
                    // 已生成的段落直接显示预览图
                    ImagePreviewDialog(
                        paragraphIndex = selectedParagraphIndex,
                        onDismiss = { showProgress = false }
                    )
                } else {
                    // 未生成的段落显示生成进度
                    FullScreenProgress(onComplete = {
                        showProgress = false
                        showPreview = true
                    })
                }
            }
            
            // 图片预览对话框
            if (showPreview) {
                ImagePreviewDialog(
                    paragraphIndex = selectedParagraphIndex,
                    onDismiss = { showPreview = false }
                )
            }
        }
    }
}

@Composable
private fun WelcomeSection(
    modifier: Modifier = Modifier,
    onUpload: () -> Unit
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // 图标
        Icon(
            imageVector = Icons.Rounded.CheckCircle, 
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier
                .size(72.dp)
                .padding(bottom = 16.dp)
        )
        
        // 欢迎标题
        Text(
            text = "欢迎使用aigc-AdGraph",
            style = MaterialTheme.typography.headlineMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onBackground
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // 副标题/说明
        Text(
            text = "上传您的文档，系统会自动为文档段落生成配图",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // 上传按钮
        Button(
            onClick = onUpload,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = ButtonShape,
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.primary
            )
        ) {
            Text(
                "选择文档",
                style = MaterialTheme.typography.titleMedium
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // 支持的格式
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = CardShape,
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Rounded.Info,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        "支持的格式",
                        style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    "txt、epub、doc、docx等常见文本格式",
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun ParagraphCard(
    text: String,
    isActive: Boolean,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val backgroundColor = when {
        isActive -> MaterialTheme.colorScheme.primaryContainer
        isSelected -> MaterialTheme.colorScheme.secondaryContainer
        else -> MaterialTheme.colorScheme.surface
    }
    
    val contentColor = when {
        isActive -> MaterialTheme.colorScheme.onPrimaryContainer
        isSelected -> MaterialTheme.colorScheme.onSecondaryContainer
        else -> MaterialTheme.colorScheme.onSurface
    }
    
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(enabled = !isActive, onClick = onClick)
            .shadow(
                elevation = if (isActive) 6.dp else 2.dp,
                shape = RoundedCornerShape(12.dp)
            ),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = backgroundColor,
            contentColor = contentColor
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            if (isActive) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        "当前处理段落",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                    
                    LinearProgressIndicator(
                        modifier = Modifier.width(100.dp),
                        color = MaterialTheme.colorScheme.primary,
                        trackColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
                    )
                }
            }
            
            Text(
                text = text,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 4,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
private fun ActiveParagraphPreview(
    index: Int,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .shadow(
                elevation = 8.dp,
                shape = RoundedCornerShape(16.dp)
            ),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
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
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                CircularProgressIndicator(
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(48.dp)
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "正在为第 ${index + 1} 段生成配图...",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun FullScreenProgress(
    onComplete: () -> Unit
) {
    var progress by remember { mutableStateOf(0f) }
    
    LaunchedEffect(Unit) {
        // 模拟进度更新
        repeat(100) {
            progress = (it + 1) / 100f
            delay(20)
        }
        delay(300)
        onComplete()
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.8f)),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier
                .width(300.dp)
                .padding(16.dp),
            shape = DialogShape,
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    "生成图片中...",
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.onSurface
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                CircularProgressIndicator(
                    progress = { progress },
                    modifier = Modifier.size(64.dp),
                    color = MaterialTheme.colorScheme.primary,
                    trackColor = MaterialTheme.colorScheme.surfaceVariant
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    "${(progress * 100).toInt()}%",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    "请稍候，AI正在为您生成精美配图",
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun ImagePreviewDialog(
    paragraphIndex: Int,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        shape = DialogShape,
        title = { 
            Text(
                "第 ${paragraphIndex + 1} 段的配图",
                style = MaterialTheme.typography.titleLarge
            ) 
        },
        text = {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .clip(RoundedCornerShape(12.dp))
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
                Text(
                    text = "此处将显示生成的配图",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = onDismiss,
                colors = ButtonDefaults.textButtonColors(
                    contentColor = MaterialTheme.colorScheme.primary
                )
            ) {
                Text("关闭")
            }
        }
    )
}