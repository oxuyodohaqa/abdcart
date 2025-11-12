# Admin Commission Settings Documentation

## Overview
The Admin Commission Settings feature allows the owner to configure how admin commissions are calculated globally. The system supports two modes: **Flat Rate** and **Bracket-Based**.

## Features

### 1. Flat Rate Mode
- A single percentage is applied to all sales profit
- Simple and straightforward calculation
- Best for consistent commission structures
- Example: 15% commission on all sales

**Formula:**
```
Commission = Profit × Flat Rate (%)
```

**Example Calculation:**
- Product buy price: ₱100
- Product sell price: ₱150
- Profit: ₱50
- Flat rate: 15%
- Admin commission: ₱50 × 15% = ₱7.50
- Owner profit: ₱50 - ₱7.50 = ₱42.50

### 2. Bracket-Based Mode
- Different percentages based on profit ranges
- Allows progressive commission structure
- Incentivizes higher-value sales
- Customizable brackets

**Formula:**
```
Commission = Profit × Bracket Rate (%)
(Rate depends on which bracket the profit falls into)
```

**Default Brackets:**
| Profit Range | Commission Rate |
|-------------|----------------|
| ₱0 - ₱299 | 10% |
| ₱300 - ₱599 | 15% |
| ₱600 - ₱999 | 20% |
| ₱1000+ | 25% |

**Example Calculations:**

*Example 1: Low profit sale*
- Profit: ₱200
- Falls in bracket: ₱0-₱299 (10%)
- Admin commission: ₱200 × 10% = ₱20
- Owner profit: ₱200 - ₱20 = ₱180

*Example 2: Medium profit sale*
- Profit: ₱500
- Falls in bracket: ₱300-₱599 (15%)
- Admin commission: ₱500 × 15% = ₱75
- Owner profit: ₱500 - ₱75 = ₱425

*Example 3: High profit sale*
- Profit: ₱1500
- Falls in bracket: ₱1000+ (25%)
- Admin commission: ₱1500 × 25% = ₱375
- Owner profit: ₱1500 - ₱375 = ₱1125

## How to Configure (Owner Only)

### Accessing Commission Settings
1. Click the **⚙️ Settings** button in the navigation bar
2. Scroll to the **💰 Admin Commission Settings** section
3. This section is only visible to the owner

### Setting Up Flat Rate Mode
1. Select **💵 Flat Rate** option
2. Enter the desired percentage (0-100)
3. Click **💾 Save Settings**
4. Changes sync instantly to all admin accounts

### Setting Up Bracket-Based Mode
1. Select **📊 Bracket-Based** option
2. Configure brackets:
   - **Min Profit**: Starting amount for the bracket (₱)
   - **Max Profit**: Ending amount for the bracket (₱) - Leave empty for infinity
   - **Rate**: Commission percentage for this bracket (0-100%)
3. Use **➕ Add Bracket** to create new brackets
4. Use **🗑️** button to remove brackets (must keep at least one)
5. Click **💾 Save Settings**
6. Changes sync instantly to all admin accounts

### Best Practices

**For Flat Rate:**
- Use for simple, consistent commission structures
- Typical range: 10-25%
- Easy to understand and calculate

**For Bracket-Based:**
- Sort brackets by profit amount (system auto-sorts)
- Avoid overlapping ranges
- Ensure all profit ranges are covered
- Last bracket should have infinity (∞) as max
- Use progressive rates to incentivize higher sales

## Real-Time Synchronization

### Instant Updates
- When the owner changes commission settings, ALL connected admins receive the update immediately
- No page refresh required
- Notification toast appears: "💰 Commission settings updated!"
- Commission badge updates automatically

### Admin View
- Admins see a badge showing current commission mode
- Badge displays:
  - "💰 Commission: 15% Flat" for flat rate mode
  - "💰 Commission: Bracket-Based" for bracket mode
- Badge is always visible in the top navigation area

### Where Commission Settings Apply
Commission settings affect:
1. **Product Display** - Shows calculated commission when viewing products
2. **Sales Recording** - Applies correct commission when recording new sales
3. **Product Calculator** - Shows commission breakdown for all admins
4. **Payout Calculations** - Determines admin earnings
5. **Sales Table** - Updates commission amounts for existing sales

## Validation Rules

### Flat Rate Mode
- Percentage must be between 0 and 100
- Cannot be empty
- Decimal values allowed (e.g., 12.5%)

### Bracket-Based Mode
- At least one bracket must exist
- Min profit must be ≥ 0
- Max profit must be > min profit (or infinity)
- Rate must be between 0 and 100
- Brackets are automatically sorted by min profit
- No overlapping ranges allowed

## Examples of Use Cases

### Use Case 1: Startup Phase
**Setup:** Flat rate at 20%
**Reason:** Simple structure, easy to understand for new admins

### Use Case 2: Growth Phase
**Setup:** Bracket-based
- 0-299: 15%
- 300-599: 18%
- 600+: 22%

**Reason:** Incentivizes admins to make higher-value sales

### Use Case 3: Mature Business
**Setup:** Bracket-based with more tiers
- 0-199: 10%
- 200-499: 15%
- 500-999: 20%
- 1000-1999: 25%
- 2000+: 30%

**Reason:** Complex progressive structure for experienced team

## Troubleshooting

### Commission Not Updating
**Problem:** Admins don't see updated commission settings
**Solution:**
1. Check internet connection
2. Verify Firebase is connected (look for "🔄 Synced" indicator)
3. Refresh the browser
4. Ensure owner saved settings correctly

### Incorrect Commission Calculated
**Problem:** Commission amount doesn't match expected value
**Solution:**
1. Verify the profit amount (sell price - buy price)
2. Check which bracket the profit falls into
3. Confirm the commission rate for that bracket
4. Recalculate manually: Profit × Rate

### Can't Save Settings
**Problem:** Error when saving commission settings
**Solution:**
1. Verify you're logged in as owner (not admin)
2. Check all bracket values are valid
3. Ensure at least one bracket exists for bracket-based mode
4. Check Firebase connection status

## Technical Details

### Data Structure
```javascript
commissionSettings: {
    mode: 'flat' | 'bracket',
    flatRate: 15,  // percentage
    brackets: [
        {
            minProfit: 0,
            maxProfit: 299,
            rate: 10
        },
        // ... more brackets
    ]
}
```

### Storage Location
- Stored in Firebase Realtime Database
- Path: `@dollyhrtzn/commissionSettings`
- Global for all users
- Real-time sync enabled

### Calculation Functions
- `calculateCommission(profit)` - Returns commission amount
- `getCommissionRate(profit)` - Returns applicable rate percentage

## Future Enhancements
Potential improvements for future versions:
- Per-admin custom commission rates (override global)
- Time-based commission changes (seasonal rates)
- Product category-specific commissions
- Tiered commission based on sales volume
- Commission history tracking
- Performance-based bonus tiers

## Support
For issues or questions about commission settings:
1. Check this documentation
2. Review the troubleshooting section
3. Contact system administrator
4. Check REALTIME_SYNC.md for sync-related issues
