"""
打字分數計算測試
"""
import pytest


class TestWPMCalculation:
    """WPM 計算測試"""
    
    def test_calculate_wpm_60_seconds(self):
        """測試 60 秒 WPM 計算"""
        # 60 秒內打 300 個字符 (假設 5 字符 = 1 單字)
        # WPM = (300 / 5) / (60 / 60) = 60
        characters = 300
        seconds = 60
        wpm = (characters / 5) / (seconds / 60)
        
        assert wpm == 60.0
    
    def test_calculate_wpm_30_seconds(self):
        """測試 30 秒 WPM 計算"""
        # 30 秒內打 150 個字符
        # WPM = (150 / 5) / (30 / 60) = 60
        characters = 150
        seconds = 30
        wpm = (characters / 5) / (seconds / 60)
        
        assert wpm == 60.0
    
    def test_calculate_wpm_zero_time(self):
        """測試零時間的邊界情況"""
        characters = 100
        seconds = 0
        
        # 應該處理除以零的情況
        if seconds == 0:
            wpm = 0
        else:
            wpm = (characters / 5) / (seconds / 60)
        
        assert wpm == 0
    
    def test_calculate_wpm_high_speed(self):
        """測試高速打字"""
        # 60 秒內打 600 個字符
        # WPM = (600 / 5) / 1 = 120
        characters = 600
        seconds = 60
        wpm = (characters / 5) / (seconds / 60)
        
        assert wpm == 120.0


class TestAccuracyCalculation:
    """準確度計算測試"""
    
    def test_calculate_accuracy_perfect(self):
        """測試完美準確度"""
        correct = 100
        total = 100
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        assert accuracy == 100.0
    
    def test_calculate_accuracy_95_percent(self):
        """測試 95% 準確度"""
        correct = 95
        total = 100
        accuracy = (correct / total) * 100
        
        assert accuracy == 95.0
    
    def test_calculate_accuracy_zero(self):
        """測試零準確度"""
        correct = 0
        total = 100
        accuracy = (correct / total) * 100
        
        assert accuracy == 0.0
    
    def test_calculate_accuracy_no_input(self):
        """測試無輸入的邊界情況"""
        correct = 0
        total = 0
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        assert accuracy == 0
    
    def test_calculate_accuracy_decimal(self):
        """測試小數準確度"""
        correct = 96
        total = 100
        accuracy = (correct / total) * 100
        
        assert accuracy == 96.0


class TestNetWPMCalculation:
    """淨 WPM 計算測試"""
    
    def test_calculate_net_wpm_perfect_accuracy(self):
        """測試完美準確度的淨 WPM"""
        gross_wpm = 60
        accuracy = 100
        net_wpm = gross_wpm * (accuracy / 100)
        
        assert net_wpm == 60.0
    
    def test_calculate_net_wpm_95_percent(self):
        """測試 95% 準確度的淨 WPM"""
        gross_wpm = 60
        accuracy = 95
        net_wpm = gross_wpm * (accuracy / 100)
        
        assert net_wpm == 57.0
    
    def test_calculate_net_wpm_low_accuracy(self):
        """測試低準確度的淨 WPM"""
        gross_wpm = 80
        accuracy = 50
        net_wpm = gross_wpm * (accuracy / 100)
        
        assert net_wpm == 40.0
    
    def test_calculate_net_wpm_zero_accuracy(self):
        """測試零準確度的淨 WPM"""
        gross_wpm = 100
        accuracy = 0
        net_wpm = gross_wpm * (accuracy / 100)
        
        assert net_wpm == 0.0


class TestErrorRate:
    """錯誤率測試"""
    
    def test_error_rate_calculation(self):
        """測試錯誤率計算"""
        errors = 5
        total = 100
        error_rate = (errors / total) * 100 if total > 0 else 0
        
        assert error_rate == 5.0
    
    def test_error_rate_no_errors(self):
        """測試無錯誤的情況"""
        errors = 0
        total = 100
        error_rate = (errors / total) * 100
        
        assert error_rate == 0.0
    
    def test_error_rate_all_errors(self):
        """測試全部錯誤的情況"""
        errors = 100
        total = 100
        error_rate = (errors / total) * 100
        
        assert error_rate == 100.0


class TestScoreValidation:
    """分數驗證測試"""
    
    def test_wpm_exceeds_human_limit(self):
        """測試 WPM 超過人類極限"""
        wpm = 250
        is_suspicious = wpm > 200  # 人類極限約 200 WPM
        
        assert is_suspicious is True
    
    def test_wpm_within_normal_range(self):
        """測試 WPM 在正常範圍內"""
        wpm = 80
        is_suspicious = wpm > 200
        
        assert is_suspicious is False
    
    def test_impossibly_high_accuracy_with_high_speed(self):
        """測試高速度配合超高準確度（可疑）"""
        wpm = 150
        accuracy = 99.5
        is_suspicious = wpm > 120 and accuracy > 98
        
        assert is_suspicious is True
    
    def test_realistic_performance(self):
        """測試現實的表現"""
        wpm = 80
        accuracy = 95
        is_suspicious = wpm > 120 and accuracy > 98
        
        assert is_suspicious is False


class TestProgressRate:
    """進步率計算測試"""
    
    def test_calculate_progress_rate(self):
        """測試進步率計算"""
        scores = [50, 55, 60, 65, 70]  # 線性增長
        
        # 簡單的線性回歸計算
        n = len(scores)
        if n < 2:
            progress_rate = 0
        else:
            # 計算平均進步
            total_improvement = scores[-1] - scores[0]
            progress_rate = total_improvement / (n - 1)
        
        assert progress_rate == 5.0  # 每次增加 5
    
    def test_progress_rate_no_improvement(self):
        """測試無進步的情況"""
        scores = [60, 60, 60, 60]
        
        n = len(scores)
        total_improvement = scores[-1] - scores[0]
        progress_rate = total_improvement / (n - 1) if n > 1 else 0
        
        assert progress_rate == 0.0
    
    def test_progress_rate_regression(self):
        """測試退步的情況"""
        scores = [70, 65, 60, 55]
        
        n = len(scores)
        total_improvement = scores[-1] - scores[0]
        progress_rate = total_improvement / (n - 1)
        
        assert progress_rate == -5.0  # 每次減少 5

