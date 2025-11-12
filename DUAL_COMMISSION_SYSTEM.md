# Dual Commission System Guide

## Overview
The Sales Tracker now supports **two commission systems** that can be selected individually for each admin:
1. **Flat Rate System**: Admin earns a fixed percentage of profit on every sale
2. **Bracket-Based System**: Commission rate is determined by profit ranges

## Key Features

### ✅ Per-Admin Configuration
- Each admin can have their own commission system
- Owner selects the system when creating a new admin
- Settings can be changed at any time by the owner

### ✅ Flexible Commission Models

#### Flat Rate System 💵
- Simple and predictable
- Admin earns a fixed percentage (e.g., 20%, 25%, 30%) on every sale
- Perfect for consistent, predictable earnings
- Example: 25% flat rate means admin always gets 25% of the profit

#### Bracket-Based System 📊
- Dynamic rates based on profit levels
- Higher profits automatically yield higher commission rates
- Encourages admins to pursue higher-value sales
- Uses the globally configured bracket ranges

### ✅ Owner Controls
- **Create Admin**: Select commission system during admin creation
- **Edit Settings**: Change commission system for existing admins anytime
- **Global Brackets**: Configure bracket ranges that apply to all bracket-based admins
- **Real-Time Sync**: All changes sync instantly across all users

## How to Use

### Creating a New Admin

1. Click **"Manage Admins"** button in the dashboard
2. Fill in admin details (name, username, password)
3. Select **Commission System**:
   - **💵 Flat Rate**: Choose this for a fixed percentage
   - **📊 Bracket-Based**: Choose this to use profit brackets
4. If Flat Rate selected:
   - Enter the percentage (e.g., 20, 25, 30)
5. If Bracket-Based selected:
   - The admin will use the configured brackets automatically
6. Click **"Add Admin"**

### Editing Commission Settings

1. In the **Admin List**, click **⚙️ Settings** next to an admin
2. The **Edit Commission Settings** modal opens
3. Toggle between **Flat Rate** and **Bracket-Based**
4. If switching to Flat Rate, enter the percentage
5. Click **"Save Changes"**
6. Changes sync immediately to all connected sessions

### Managing Commission Brackets

Brackets apply to **all admins using the Bracket-Based system**:

1. Scroll to **Commission Bracket System** section
2. View existing brackets with their ranges and rates
3. Click **"Add Bracket"** to create new ranges
4. Delete unwanted brackets using the 🗑️ button
5. Brackets automatically sort by profit range

**Default Brackets:**
- ₱0 - ₱299.99: 10% commission
- ₱300 - ₱599.99: 15% commission
- ₱600 - ₱999.99: 20% commission
- ₱1000+: 25% commission

## Examples

### Example 1: Flat Rate Admin (25%)

**Admin**: Sarah Johnson  
**Commission System**: Flat Rate 25%

**Sale 1:**
- Sell Price: ₱500
- Buy Price: ₱200
- Profit: ₱300
- **Commission: ₱75** (₱300 × 25%)

**Sale 2:**
- Sell Price: ₱2000
- Buy Price: ₱500
- Profit: ₱1500
- **Commission: ₱375** (₱1500 × 25%)

*Every sale earns exactly 25% of profit, regardless of amount.*

### Example 2: Bracket-Based Admin

**Admin**: Mike Chen  
**Commission System**: Bracket-Based

**Sale 1:**
- Sell Price: ₱500
- Buy Price: ₱200
- Profit: ₱300
- Applicable Bracket: ₱300-₱599.99 → 15%
- **Commission: ₱45** (₱300 × 15%)

**Sale 2:**
- Sell Price: ₱2000
- Buy Price: ₱500
- Profit: ₱1500
- Applicable Bracket: ₱1000+ → 25%
- **Commission: ₱375** (₱1500 × 25%)

*Commission rate increases with profit, incentivizing higher-value sales.*

### Example 3: Mixed Team

**Team Setup:**
- Sarah (Flat Rate 25%): Good for consistent performance
- Mike (Bracket-Based): Motivated by higher-value sales
- Emily (Flat Rate 30%): Premium rate for experienced seller

Each admin's earnings are calculated using their assigned system.

## Admin View

### What Admins See
- Their current commission system type (Flat Rate or Bracket-Based)
- Commission earned per sale
- Total earnings across all sales
- Cannot modify their own commission settings (owner only)

### Commission Display
In the admin list, each admin shows:
- **💵 Flat Rate: XX%** for flat rate admins
- **📊 Bracket-Based** for bracket-based admins

## Real-Time Synchronization

All commission settings sync in real-time:

1. **Owner changes flat rate**: Admin immediately sees new rate on next sale
2. **Owner switches system**: Takes effect on the next sale recorded
3. **Owner updates brackets**: All bracket-based admins use new ranges instantly
4. **Multiple owners logged in**: All see changes immediately

## Database Structure

### User Object
```javascript
{
  id: 123456,
  username: "john_sales",
  customName: "John Doe",
  role: "admin",
  commissionMode: "flatRate", // or "bracket"
  profitPercent: 25, // Used only if flatRate
  createdDate: "2024-01-15"
}
```

### Backward Compatibility
- Existing admins without `commissionMode` default to **Flat Rate**
- Existing `profitPercent` values are preserved
- No data migration needed

## Technical Details

### Commission Calculation Function
```javascript
function getCommissionRateForProfit(profit, userId) {
  const user = userId ? users.find(u => u.id === userId) : currentSession;
  
  // Flat Rate Mode
  if (user && user.commissionMode === 'flatRate') {
    return user.profitPercent || 20;
  }
  
  // Bracket-Based Mode
  for (let bracket of commissionBrackets) {
    if (profit >= bracket.minProfit && 
        (bracket.maxProfit === null || profit <= bracket.maxProfit)) {
      return bracket.rate;
    }
  }
  
  return user ? (user.profitPercent || 25) : 25;
}
```

### Real-Time Listeners
- Commission brackets: `@dollyhrtzn/settings/{owner}/commissionBrackets`
- User settings: `@dollyhrtzn/users/{username}`
- All changes propagate via Firebase real-time listeners

## Benefits

### For Owners
✅ Flexibility to match commission to admin performance  
✅ Ability to test different commission structures  
✅ Easy to adjust as business needs change  
✅ Control over individual admin motivation strategies  

### For Admins
✅ Clear understanding of how they earn  
✅ Flat rate provides predictability  
✅ Bracket system rewards higher-value sales  
✅ Fair and transparent commission structure  

## Best Practices

### When to Use Flat Rate
- New admins learning the system
- Admins with consistent product mix
- When simplicity is preferred
- For premium/experienced sellers (higher flat rate)

### When to Use Bracket-Based
- To incentivize higher-value sales
- For competitive sales teams
- When product mix varies significantly
- To reward performance improvements

### Transitioning Between Systems
1. Monitor admin performance with current system
2. Communicate planned changes to affected admins
3. Use "Settings" button to switch commission mode
4. Track results and adjust as needed

## Troubleshooting

### Issue: Admin shows wrong commission rate
**Solution**: Check that owner hasn't recently changed settings. Refresh page to ensure latest data is loaded.

### Issue: Bracket-based admin gets unexpected rate
**Solution**: Verify profit calculation (Sell Price - Buy Price). Check which bracket the profit falls into.

### Issue: Changes not syncing
**Solution**: Check Firebase connection status (sync indicator in top-right). Ensure internet connection is stable.

### Issue: Can't edit commission settings
**Solution**: Only the owner can edit commission settings. Verify you're logged in as owner, not admin.

## Security

### Access Control
- ❌ Admins **cannot** view other admins' commission rates
- ❌ Admins **cannot** modify their own commission settings
- ❌ Admins **cannot** modify commission brackets
- ✅ Only owner can create, edit, and manage all commission settings

### Data Protection
- Commission settings stored securely in Firebase
- Role-based authentication enforced
- All changes logged with timestamps

## Future Enhancements

Potential improvements for future versions:
- [ ] Commission history tracking per admin
- [ ] Performance-based automatic rate adjustments
- [ ] Temporary commission boosts/promotions
- [ ] Commission simulation/preview tools
- [ ] Export commission reports
- [ ] Per-product commission overrides

## Summary

The dual commission system provides:
- **Flexibility**: Choose the right system for each admin
- **Control**: Owner manages all commission settings
- **Transparency**: Clear display of commission modes
- **Real-Time**: Instant synchronization of all changes
- **Simplicity**: Easy to understand and use

This feature empowers owners to optimize their team's motivation and earnings while maintaining full control over the commission structure.
