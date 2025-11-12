# Commission Bracket System Guide

## Overview
The commission bracket system allows owners to set different commission rates based on profit ranges. This incentivizes higher-profit sales with better commission rates.

## How It Works

### Formula
1. **Profit Calculation**: `Profit = Sales Price - Capital (Buy Price)`
2. **Salary Calculation**: `Salary = Profit × Commission Rate (%)`

### Default Brackets
When no custom brackets are configured, the system uses these defaults:
- **₱0 - ₱299.99**: 10% commission
- **₱300 - ₱599.99**: 15% commission
- **₱600 - ₱999.99**: 20% commission
- **₱1000+**: 25% commission

### Example Calculations

#### Example 1: Low Profit Sale
- Sell Price: ₱250
- Buy Price: ₱150
- **Profit**: ₱100 (₱250 - ₱150)
- **Commission Rate**: 10% (falls in ₱0-299.99 bracket)
- **Admin Salary**: ₱10 (₱100 × 10%)
- **Owner Profit**: ₱90 (₱100 - ₱10)

#### Example 2: Medium Profit Sale
- Sell Price: ₱500
- Buy Price: ₱200
- **Profit**: ₱300 (₱500 - ₱200)
- **Commission Rate**: 15% (falls in ₱300-599.99 bracket)
- **Admin Salary**: ₱45 (₱300 × 15%)
- **Owner Profit**: ₱255 (₱300 - ₱45)

#### Example 3: High Profit Sale
- Sell Price: ₱1500
- Buy Price: ₱300
- **Profit**: ₱1200 (₱1500 - ₱300)
- **Commission Rate**: 25% (falls in ₱1000+ bracket)
- **Admin Salary**: ₱300 (₱1200 × 25%)
- **Owner Profit**: ₱900 (₱1200 - ₱300)

## Configuration (Owner Only)

### Adding Brackets
1. Navigate to **Manage Admins** modal
2. Scroll to **Commission Bracket System** section
3. Click **Add Bracket** button
4. Fill in:
   - **Minimum Profit**: Starting amount for this bracket (e.g., 0, 300, 600)
   - **Maximum Profit**: Ending amount (leave empty for "and above")
   - **Commission Rate**: Percentage for this range (0-100%)
5. Click **Add Bracket**

### Managing Brackets
- Brackets are automatically sorted by minimum profit
- Delete unwanted brackets using the 🗑️ button
- All brackets sync in real-time to all connected admins
- Admins see the applicable rate but cannot modify brackets

## Features

### For Owners
✅ Full control over commission structure
✅ Real-time sync to all admins
✅ Flexible bracket configuration
✅ Automatic payout calculations based on brackets
✅ Visual feedback in payout dashboard

### For Admins
✅ Automatic rate calculation based on sale profit
✅ Commission displayed during sale entry
✅ Cannot modify rates or prices (owner-controlled)
✅ Clear visibility of earnings per sale

## Security & Validation

### Owner-Only Actions
- ❌ Admins **cannot** add/edit/delete brackets
- ❌ Admins **cannot** modify product prices
- ❌ Admins **cannot** delete products
- ✅ Admins **can** view products and record sales

### Data Integrity
- All brackets stored in Firebase under owner's settings
- Real-time synchronization ensures consistency
- Bracket system applies to all new sales automatically
- Historical sales maintain their original commission rates

## Testing Verification

The implementation has been verified with these test cases:

| Profit Amount | Expected Rate | Result |
|--------------|---------------|---------|
| ₱100 | 10% | ✅ Pass |
| ₱299.99 | 10% | ✅ Pass |
| ₱300 | 15% | ✅ Pass |
| ₱450 | 15% | ✅ Pass |
| ₱600 | 20% | ✅ Pass |
| ₱800 | 20% | ✅ Pass |
| ₱1000 | 25% | ✅ Pass |
| ₱5000 | 25% | ✅ Pass |

## Troubleshooting

### Brackets Not Showing
- Ensure you're logged in as **owner**
- Check Firebase connection (sync indicator)
- Refresh the page

### Wrong Commission Rate Applied
- Verify bracket ranges don't overlap
- Check that profit calculation is correct (Sell Price - Buy Price)
- Ensure brackets are saved (green checkmark)

### Admin Cannot See Rates
- Brackets are loaded for all users
- Admins see rates applied but cannot edit
- Check connection status in top-right corner

## Best Practices

1. **Set Clear Brackets**: Use round numbers for easy understanding
2. **Motivate Performance**: Higher profits = higher rates
3. **Regular Review**: Adjust brackets based on business needs
4. **Communicate Changes**: Inform admins about bracket updates
5. **Monitor Payouts**: Use payout dashboard to track earnings

## Technical Implementation

### Key Functions
- `getCommissionRateForProfit(profit)`: Returns applicable rate
- `loadCommissionBrackets()`: Syncs brackets from Firebase
- `saveCommissionBrackets()`: Saves bracket configuration
- `renderCommissionBrackets()`: Displays bracket list

### Database Structure
```
@dollyhrtzn/
  └── settings/
      └── {ownerUsername}/
          └── commissionBrackets/
              ├── 0: { id, minProfit, maxProfit, rate }
              ├── 1: { id, minProfit, maxProfit, rate }
              └── ...
```

### Real-Time Sync
- Brackets loaded on login
- Changes propagate instantly
- All connected users updated automatically
- Visual sync indicator shows status

## Support

For issues or questions about the commission bracket system:
1. Check this guide first
2. Verify Firebase connection
3. Review browser console for errors
4. Contact system administrator
