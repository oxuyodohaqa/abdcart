# Real-Time Sync Architecture

## Overview
This application uses Firebase Realtime Database to provide automatic synchronization of data between admin and owner accounts. All changes are reflected instantly across all connected users without requiring manual refresh.

## Architecture

### Database Structure
```
@dollyhrtzn/
├── users/
│   └── {username}/          # User profiles and settings
├── sales/
│   └── {username}/          # Sales records per user
│       └── {saleId}/        # Individual sale data
├── products/
│   └── {productId}/         # Product catalog
├── subscriptionProducts/
│   └── {productId}/         # Subscription-based products
├── payouts/
│   └── {payoutId}/          # Payout records
├── accounts/
│   └── {accountId}/         # Streaming service accounts
├── settings/
│   └── {username}/          # User-specific settings
└── payoutHistory/
    └── {historyId}/         # Historical payout records
```

## Real-Time Listeners

### Data Synchronization
The application uses Firebase's `.on('value')` event listeners for real-time data synchronization:

1. **Users** - Tracks admin accounts and permissions
2. **Sales** - Monitors all sales transactions across admins
3. **Products** - Keeps product catalog in sync
4. **Subscription Products** - Manages subscription-based offerings
5. **Payouts** - Tracks pending and completed payouts
6. **Accounts** - Manages streaming service accounts
7. **Settings** - Syncs user preferences and theme settings

### Connection State Monitoring
The application monitors Firebase connection state using:
```javascript
database.ref('.info/connected').on('value', (snapshot) => {
    isConnected = snapshot.val() === true;
});
```

## Visual Feedback

### Sync Status Indicator
Located in the top-right corner of the application:

- **🔄 Synced** (Green) - Connected and synchronized
- **⏳ Syncing...** (Yellow) - Data is being written/updated
- **❌ Offline** (Red) - Disconnected from Firebase

### Real-Time Updates
When data changes occur:
1. The sync indicator shows "Syncing..."
2. Data is written to Firebase
3. All connected clients receive the update via listeners
4. UI automatically re-renders with new data
5. Sync indicator returns to "Synced"

## Data Flow

### Owner Actions
```
Owner Updates Product Price
    ↓
Firebase Database Updated
    ↓
All Connected Admins Notified
    ↓
Admin Dashboards Auto-Update
```

### Admin Actions
```
Admin Records Sale
    ↓
Firebase Database Updated
    ↓
Owner Dashboard Notified
    ↓
Statistics Auto-Recalculate
    ↓
Payout Amounts Auto-Update
```

## Key Features

### Automatic Synchronization
- No manual refresh required
- Changes propagate instantly
- Works across multiple devices and sessions

### Global Consistency
- Single source of truth (Firebase)
- All users see the same data
- No data conflicts or race conditions

### Offline Resilience
- Connection state monitoring
- Visual feedback for connection status
- Automatic reconnection on network restore

## Implementation Details

### Settings Real-Time Sync
Previously, settings were loaded once using `.once()`. Now they use `.on()` for continuous synchronization:

```javascript
// Old approach (no real-time sync)
getRef('settings/' + currentUsername).once('value').then((snapshot) => {
    settings = snapshot.val();
});

// New approach (real-time sync)
getRef('settings/' + currentUsername).on('value', (snapshot) => {
    if (snapshot.exists()) {
        settings = snapshot.val();
        applySettings();
    }
});
```

### Write Operations with Sync Indicators
All data write operations show visual feedback:

```javascript
showSyncingIndicator();  // Show "Syncing..." status
getRef('products/' + productId).set(product)
    .then(() => {
        // Automatically returns to "Synced" status
        showToast('✅ Product updated!', 'success');
    });
```

## Benefits

### For Owners
- Monitor all admin activities in real-time
- See sales as they happen
- Instant visibility into inventory changes
- Automatic payout calculations

### For Admins
- Always see latest product prices
- Immediate commission rate updates
- Real-time inventory status
- Synchronized sales tracking

## Technical Considerations

### Performance
- Firebase handles thousands of concurrent connections
- Efficient delta updates (only changed data is transmitted)
- Automatic data caching for offline scenarios

### Security
- Firebase security rules control data access
- User authentication via username/password
- Role-based permissions (owner vs admin)

### Scalability
- Serverless architecture via Firebase
- Automatic scaling based on usage
- No infrastructure management required

## Future Enhancements

Possible improvements for real-time sync:
- Presence system (show who's online)
- Real-time notifications for important events
- Conflict resolution for simultaneous edits
- Offline data queuing and sync on reconnect
- WebSocket fallback for restricted networks

## Troubleshooting

### Sync Indicator Shows "Offline"
1. Check internet connection
2. Verify Firebase configuration is correct
3. Check browser console for errors
4. Ensure Firebase service is operational

### Data Not Updating
1. Verify connection status (check sync indicator)
2. Clear browser cache and reload
3. Check Firebase security rules
4. Verify user has proper permissions

### Performance Issues
1. Limit the amount of data loaded initially
2. Use pagination for large datasets
3. Unsubscribe from listeners when not needed
4. Check network latency

## Resources

- [Firebase Realtime Database Documentation](https://firebase.google.com/docs/database)
- [Best Practices for Firebase](https://firebase.google.com/docs/database/web/structure-data)
- [Offline Capabilities](https://firebase.google.com/docs/database/web/offline-capabilities)
