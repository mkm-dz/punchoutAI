# Punchout AI Learning Verification Script
# Checks if the agent is learning by analyzing reward trends

param(
    [int]$Window = 50,
    [string]$LogFile = "CrystalJoe.log"
)

function Get-RewardsFromLog {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        Write-Error "Log file not found: $FilePath"
        return @()
    }
    
    $rewards = @()
    $lines = Get-Content $FilePath
    
    foreach ($line in $lines) {
        try {
            # Parse: "Episode X: Reward=Y.ZZ, Steps=N"
            if ($line -match 'Reward=([^,]+)') {
                $reward = [double]$matches[1]
                $rewards += $reward
            }
        }
        catch {
            # Skip unparseable lines
        }
    }
    
    return $rewards
}

function Show-RecentRewards {
    param(
        [double[]]$Rewards,
        [int]$Count = 50
    )
    
    if ($Rewards.Count -lt $Count) {
        $Count = $Rewards.Count
    }
    
    Write-Host "`n=== RECENT $Count EPISODES ===" -ForegroundColor Cyan
    $recent = $Rewards[-$Count..-1]
    
    foreach ($i in 0..($recent.Count - 1)) {
        $episodeNum = $Rewards.Count - $Count + $i + 1
        $reward = $recent[$i]
        
        # Color code rewards
        if ($reward -gt 20) {
            $color = "Green"
        } elseif ($reward -gt 0) {
            $color = "Yellow"
        } else {
            $color = "Red"
        }
        
        Write-Host "Episode $episodeNum : $reward" -ForegroundColor $color
    }
}

function Get-MovingAverage {
    param(
        [double[]]$Rewards,
        [int]$Window = 10
    )
    
    $moving_avg = @()
    
    for ($i = 0; $i -le $Rewards.Count - $Window; $i++) {
        $sum = 0
        for ($j = 0; $j -lt $Window; $j++) {
            $sum += $Rewards[$i + $j]
        }
        $moving_avg += ($sum / $Window)
    }
    
    return $moving_avg
}

function Analyze-Learning {
    param([double[]]$Rewards)
    
    if ($Rewards.Count -lt 50) {
        Write-Host "`n⚠️  Not enough episodes yet (need 50+, have $($Rewards.Count))" -ForegroundColor Yellow
        return
    }
    
    $first50 = $Rewards[0..49]
    $last50 = $Rewards[-50..-1]
    
    $first50_avg = ($first50 | Measure-Object -Average).Average
    $last50_avg = ($last50 | Measure-Object -Average).Average
    $improvement = $last50_avg - $first50_avg
    
    Write-Host "`n=== LEARNING ANALYSIS ===" -ForegroundColor Cyan
    Write-Host "First 50 episodes average  : $([math]::Round($first50_avg, 2))" -ForegroundColor Yellow
    Write-Host "Last 50 episodes average   : $([math]::Round($last50_avg, 2))" -ForegroundColor Yellow
    Write-Host "Improvement                : $([math]::Round($improvement, 2))" -ForegroundColor Cyan
    
    Write-Host "=== VERDICT ===" -ForegroundColor Cyan
    
    if ($improvement -gt 15) {
        Write-Host "[GOOD] LEARNING WELL - Strong improvement detected!" -ForegroundColor Green
    } elseif ($improvement -gt 5) {
        Write-Host "[OK] LEARNING - Gradual improvement" -ForegroundColor Yellow
    } elseif ($improvement -gt 0) {
        Write-Host "[SLOW] LEARNING SLOW - Minimal improvement, may need adjustment" -ForegroundColor Yellow
    } elseif ($improvement -gt -5) {
        Write-Host "[BAD] NOT LEARNING - Flat or declining, check configuration" -ForegroundColor Red
    } else {
        Write-Host "[FAIL] DEGRADING - Performance getting worse" -ForegroundColor Red
    }
}

# Main execution
Write-Host "Punchout AI Learning Verification" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Get rewards from log
$rewards = Get-RewardsFromLog -FilePath $LogFile

if ($rewards.Count -eq 0) {
    Write-Error "No rewards found in log file"
    exit 1
}

Write-Host "`nTotal episodes: $($rewards.Count)" -ForegroundColor Green

# Show recent episodes
Show-RecentRewards -Rewards $rewards -Count 20

# Calculate and show moving average
$movingAvg = Get-MovingAverage -Rewards $rewards -Window 10
Write-Host "`n=== MOVING AVERAGE - 10 EPISODE WINDOW ===" -ForegroundColor Cyan
Write-Host "First: $([math]::Round($movingAvg[0], 2))"
Write-Host "Last:  $([math]::Round($movingAvg[-1], 2))"

# Analyze learning
Analyze-Learning -Rewards $rewards

# Statistics
Write-Host "`n=== STATISTICS ===" -ForegroundColor Cyan
$stats = $rewards | Measure-Object -Average -Minimum -Maximum
Write-Host "Average reward : $([math]::Round($stats.Average, 2))"
Write-Host "Min reward     : $([math]::Round($stats.Minimum, 2))"
Write-Host "Max reward     : $([math]::Round($stats.Maximum, 2))"

# Count positive episodes
$positive = @($rewards | Where-Object { $_ -gt 0 }).Count
Write-Host "Positive episodes : $positive / $($rewards.Count)"

Write-Host "" -ForegroundColor Cyan
