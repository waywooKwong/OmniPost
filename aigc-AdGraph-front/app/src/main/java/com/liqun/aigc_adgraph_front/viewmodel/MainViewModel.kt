package com.liqun.aigc_adgraph_front.viewmodel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import com.liqun.aigc_adgraph_front.model.NovelData

class MainViewModel : ViewModel() {
    var isProcessing by mutableStateOf(false)
        private set
    
    var currentParagraphIndex by mutableStateOf(0)
        private set
    
    var isPaused by mutableStateOf(false)
        private set
    
    var selectedParagraphIndex by mutableStateOf(-1)
        private set
    
    var showPreviewScreen by mutableStateOf(false)
        private set
    
    var showProgress by mutableStateOf(false)
        private set
    
    var generatedImages by mutableStateOf(List(NovelData.paragraphs.size) { "" })
        private set
    
    fun startProcessing() {
        isProcessing = true
    }
    
    fun togglePause() {
        isPaused = !isPaused
    }
    
    fun updateCurrentParagraph() {
        if (!isPaused && currentParagraphIndex < NovelData.paragraphs.size) {
            currentParagraphIndex = (currentParagraphIndex + 1) % NovelData.paragraphs.size
        }
    }
    
    fun selectParagraph(index: Int) {
        selectedParagraphIndex = index
    }
    
    fun showPreview() {
        showPreviewScreen = true
    }
    
    fun hidePreview() {
        showPreviewScreen = false
    }
    
    fun toggleProgress() {
        showProgress = !showProgress
    }
    
    fun updateGeneratedImage(index: Int, imageUrl: String) {
        generatedImages = generatedImages.toMutableList().apply {
            set(index, imageUrl)
        }
    }
}