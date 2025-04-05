export class SyncService {
  // Sync local model weights with the server using differential privacy
  static async syncWithServer(syncSettings, progressCallback) {
    try {
      // Check if model is loaded
      const modelStatus = await fetch('http://localhost:8000/api/model/status');
      const modelData = await modelStatus.json();
      
      if (!modelData.is_loaded) {
        throw new Error('No model loaded. Please download a model before syncing.');
      }
      
      // Start the sync process
      const response = await fetch('http://localhost:8000/api/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          privacy_settings: {
            epsilon: syncSettings.privacyEpsilon,
            delta: syncSettings.privacyDelta
          },
          sync_frequency: syncSettings.syncFrequency
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Sync failed to start');
      }
      
      const data = await response.json();
      const syncId = data.sync_id;
      
      // Poll for sync progress
      return new Promise((resolve, reject) => {
        const checkProgress = async () => {
          try {
            const progressResponse = await fetch(`http://localhost:8000/api/sync/${syncId}/progress`);
            
            if (!progressResponse.ok) {
              throw new Error('Failed to check sync progress');
            }
            
            const progressData = await progressResponse.json();
            
            if (progressCallback) {
              progressCallback(progressData.progress);
            }
            
            if (progressData.status === 'completed') {
              resolve(progressData);
            } else if (progressData.status === 'failed') {
              reject(new Error(progressData.error || 'Sync failed'));
            } else {
              // Continue polling
              setTimeout(checkProgress, 1000);
            }
          } catch (error) {
            reject(error);
          }
        };
        
        // Start checking progress
        checkProgress();
      });
    } catch (error) {
      console.error('Error syncing with server:', error);
      
      // Simulate sync for demo purposes when server is down
      if (error.message.includes('Failed to fetch')) {
        return new Promise((resolve) => {
          let progress = 0;
          const interval = setInterval(() => {
            progress += 10;
            if (progressCallback) {
              progressCallback(progress > 100 ? 100 : progress);
            }
            
            if (progress >= 100) {
              clearInterval(interval);
              resolve({ status: 'completed', progress: 100 });
            }
          }, 500);
        });
      }
      
      throw error;
    }
  }
  
  // Check the last sync status
  static async getLastSyncStatus() {
    try {
      const response = await fetch('http://localhost:8000/api/sync/status');
      
      if (!response.ok) {
        throw new Error('Failed to get sync status');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting sync status:', error);
      
      // Return default status if server is unreachable
      return {
        last_sync_time: null,
        sync_successful: false,
        gradient_updates_sent: 0,
        server_updates_received: 0
      };
    }
  }
  
  // Get configured sync schedule
  static async getSyncSchedule() {
    try {
      const response = await fetch('http://localhost:8000/api/sync/schedule');
      
      if (!response.ok) {
        throw new Error('Failed to get sync schedule');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error getting sync schedule:', error);
      
      // Return default schedule if server is unreachable
      const syncSettings = localStorage.getItem('syncSettings');
      if (syncSettings) {
        const settings = JSON.parse(syncSettings);
        return {
          frequency: settings.syncFrequency,
          next_sync_time: null,
          enabled: settings.syncFrequency !== 'manual'
        };
      }
      
      return {
        frequency: 'manual',
        next_sync_time: null,
        enabled: false
      };
    }
  }
}
