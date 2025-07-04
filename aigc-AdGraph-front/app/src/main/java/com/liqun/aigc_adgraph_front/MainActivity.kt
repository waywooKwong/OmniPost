package com.liqun.aigc_adgraph_front

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.liqun.aigc_adgraph_front.model.NovelData
import com.liqun.aigc_adgraph_front.ui.screens.MainScreen
import com.liqun.aigc_adgraph_front.ui.screens.PreviewScreen
import com.liqun.aigc_adgraph_front.ui.theme.AigcAdGraphFrontTheme

class MainActivity : ComponentActivity() {
    // 预览状态跟踪
    private val showPreviewState = mutableStateOf(false)
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 加载资源数据
        try {
            NovelData.loadData(this)
            Log.d("MainActivity", "加载资源数据成功，段落数: ${NovelData.paragraphs.size}")
        } catch (e: Exception) {
            Log.e("MainActivity", "加载资源数据失败", e)
        }
        
        // 注册返回键处理
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                // 如果当前在预览界面，返回到主界面
                if (showPreviewState.value) {
                    Log.d("MainActivity", "返回键按下: 从预览返回到主界面")
                    showPreviewState.value = false
                } else {
                    // 否则，允许默认返回行为（退出应用）
                    Log.d("MainActivity", "返回键按下: 退出应用")
                    isEnabled = false
                    onBackPressedDispatcher.onBackPressed()
                }
            }
        })
        
        setContent {
            MainActivityContent()
        }
    }
    
    @Composable
    private fun MainActivityContent() {
        AigcAdGraphFrontTheme {
            Surface(
                modifier = Modifier.fillMaxSize()
            ) {
                var showPreview by remember { showPreviewState }
                
                if (showPreview) {
                    PreviewScreen(
                        onBack = {
                            Log.d("MainActivity", "PreviewScreen 返回按钮点击")
                            showPreview = false
                        }
                    )
                } else {
                    MainScreen(
                        onPreview = {
                            Log.d("MainActivity", "切换到预览界面")
                            showPreview = true
                        }
                    )
                }
            }
        }
    }
}

