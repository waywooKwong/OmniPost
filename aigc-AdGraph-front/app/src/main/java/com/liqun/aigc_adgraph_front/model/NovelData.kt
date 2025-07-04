package com.liqun.aigc_adgraph_front.model

import android.content.Context
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.IOException

@Serializable
data class ImageInfo(
    val id: String,
    val description: String,
    val file: String
)

@Serializable
data class NovelDataModel(
    val paragraphs: List<String> = emptyList(),
    val images: List<ImageInfo> = emptyList()
)

object NovelData {
    // 默认数据，作为后备
    private val defaultData = listOf(
        "清晨，阳光透过窗帘洒在书桌上，小明正专注地写着作业。他的笔尖在纸上轻快地划过，留下一行行整齐的字迹。",
        "突然，一阵清脆的鸟鸣声传来，小明抬起头，看见一只彩色的小鸟停在窗台上。它歪着头，好奇地打量着屋内的一切。",
        "小明轻轻地站起来，想要靠近那只小鸟。但就在他刚迈出一步时，小鸟扑闪着翅膀飞走了，只留下几片羽毛在阳光下闪闪发亮。",
        "望着小鸟远去的方向，小明若有所思。这短暂的邂逅让他想起了昨天老师讲的课文，关于人与自然和谐相处的故事。",
        "回到书桌前，小明提起笔，开始写起了作文。这次的题目是'我的一次特别经历'，他决定把刚才与小鸟相遇的故事记录下来。"
    )
    
    // 当前加载的段落数据
    private var _paragraphs = defaultData
    
    // 当前加载的图片信息
    private var _images = listOf<ImageInfo>()
    
    // 公开的只读属性
    val paragraphs: List<String> get() = _paragraphs
    val images: List<ImageInfo> get() = _images
    
    // 资源文件路径
    private const val JSON_FILE_PATH = "json/novel_data.json"
    
    // 获取段落对应的图片资源名称
    fun getParagraphImageName(index: Int): String {
        return if (index < _images.size) {
            _images[index].file.substringBeforeLast(".")
        } else {
            "paragraph${index + 1}"
        }
    }
    
    // 获取段落对应的图片描述
    fun getParagraphImageDescription(index: Int): String {
        return if (index < _images.size) {
            _images[index].description
        } else {
            "段落 ${index + 1} 的配图"
        }
    }
    
    // 从内部assets文件夹加载数据
    fun loadData(context: Context) {
        try {
            // 从assets文件夹加载JSON数据
            context.assets.open(JSON_FILE_PATH).use { inputStream ->
                val jsonContent = inputStream.bufferedReader().use { it.readText() }
                val data = Json.decodeFromString<NovelDataModel>(jsonContent)
                if (data.paragraphs.isNotEmpty()) {
                    _paragraphs = data.paragraphs
                }
                if (data.images.isNotEmpty()) {
                    _images = data.images
                }
            }
        } catch (e: IOException) {
            e.printStackTrace()
            // 加载失败时使用默认数据
            _paragraphs = defaultData
            _images = emptyList()
        }
    }
}