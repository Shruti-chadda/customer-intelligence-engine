"""
utils.py - Helper Functions for InsightEngine
Segment naming, marketing message generation, decision engine
"""

import random
from typing import Dict, Optional


# ─────────────────────────────────────────────
# SEGMENT META-DATA
# ─────────────────────────────────────────────

SEGMENT_META = {
    "Champions": {
        "emoji":       "🏆",
        "color":       "#A8D5BA",   # pastel green
        "description": "Bought recently, buy often, and spend the most.",
        "action":      "Reward them. Make them brand ambassadors.",
        "priority":    "High",
    },
    "Loyal Customers": {
        "emoji":       "💚",
        "color":       "#B5EAD7",
        "description": "Spend a good amount, buy regularly.",
        "action":      "Upsell higher value products. Engage them actively.",
        "priority":    "High",
    },
    "Recent Customers": {
        "emoji":       "🌱",
        "color":       "#C7CEEA",
        "description": "Bought most recently, but not often.",
        "action":      "Provide onboarding value. Build the relationship.",
        "priority":    "Medium",
    },
    "Potential Loyalists": {
        "emoji":       "⭐",
        "color":       "#FFD6A5",
        "description": "Recent customers with average frequency.",
        "action":      "Offer membership or loyalty programs.",
        "priority":    "Medium",
    },
    "Promising": {
        "emoji":       "🌟",
        "color":       "#FFDAC1",
        "description": "Recent shoppers but haven't spent much.",
        "action":      "Create brand awareness, offer free trials.",
        "priority":    "Medium",
    },
    "Needs Attention": {
        "emoji":       "⚠️",
        "color":       "#FDFFB6",
        "description": "Above average recency, frequency & monetary values.",
        "action":      "Make limited time offers based on past purchases.",
        "priority":    "Medium",
    },
    "At Risk": {
        "emoji":       "🔴",
        "color":       "#FFB3B3",
        "description": "Spent big money and purchased often, but long ago.",
        "action":      "Send personalised emails to reconnect. Offer renewals.",
        "priority":    "Critical",
    },
    "Cant Lose Them": {
        "emoji":       "🆘",
        "color":       "#FF9AA2",
        "description": "Made biggest purchases, and often, but haven't returned.",
        "action":      "Win them back. Ignore them and you'll lose them forever.",
        "priority":    "Critical",
    },
    "Hibernating": {
        "emoji":       "😴",
        "color":       "#E2CFC4",
        "description": "Last purchase was a long time ago with low frequency.",
        "action":      "Offer relevant products and special discounts.",
        "priority":    "Low",
    },
    "Lost": {
        "emoji":       "💤",
        "color":       "#D4D4D4",
        "description": "Lowest recency, frequency, and monetary scores.",
        "action":      "Revive interest with outreach campaign or accept as lost.",
        "priority":    "Low",
    },
}


def get_segment_meta(segment: str) -> Dict:
    return SEGMENT_META.get(segment, {
        "emoji":       "❓",
        "color":       "#EDE9E3",
        "description": "Uncategorized segment.",
        "action":      "Analyze further.",
        "priority":    "Unknown",
    })


# ─────────────────────────────────────────────
# CAMPAIGN MESSAGE GENERATOR
# ─────────────────────────────────────────────

CAMPAIGN_TEMPLATES = {
    "Champions": [
        "🏆 {name}, you're one of our TOP customers! As a VIP, enjoy EXCLUSIVE early access to our newest collection + a complimentary gift on your next order.",
        "🎖️ Elite member {name} — your loyalty means everything to us! Here's a curated selection just for you, plus free express shipping on your next 3 orders.",
        "👑 {name}, you've earned Champion status! Unlock your exclusive {discount}% reward on premium products — limited to Champions only.",
    ],
    "Loyal Customers": [
        "💚 {name}, your loyalty is truly appreciated! Enjoy a special {discount}% discount as our way of saying thank you.",
        "🎁 Hey {name}! You've been amazing. We're giving you early access to our loyalty sale — {discount}% off storewide!",
        "✨ {name}, you're a valued member of our community! Here's a personalized offer: {discount}% off your favourite categories this week.",
    ],
    "Recent Customers": [
        "🌱 Welcome back, {name}! We loved having you. Explore what's new and enjoy {discount}% off your second purchase.",
        "👋 Hi {name}! We hope you loved your first experience. Here's a thank-you coupon: {discount}% off your next visit.",
        "🛍️ {name}, great to see you! Since you're new, here's a special treat — {discount}% off when you shop again within 7 days.",
    ],
    "Potential Loyalists": [
        "⭐ {name}, you're on the right track! Join our loyalty club today and instantly unlock {discount}% off + exclusive member perks.",
        "🚀 Almost there, {name}! One more purchase and you unlock VIP status. Plus, here's {discount}% off to get you started.",
        "🎯 {name}, we see your potential! Enjoy a special {discount}% loyalty bonus this week — just for you.",
    ],
    "Promising": [
        "🌟 {name}, you're just getting started and we love it! Here's {discount}% off to make your next visit even better.",
        "✨ Hey {name}! Discover our best sellers with an exclusive {discount}% new-customer offer. Happy shopping!",
        "🎉 {name}, big things ahead! We're offering {discount}% off to help you explore everything we have to offer.",
    ],
    "Needs Attention": [
        "⚡ {name}, it's been a while! We have new arrivals we think you'll love — and a time-sensitive {discount}% offer just for you.",
        "🔔 Hey {name}! Don't miss out. Grab {discount}% off before this exclusive offer expires in 48 hours.",
        "💡 {name}, we noticed you haven't visited recently. Come back and save {discount}% on your next purchase — offer valid this week only.",
    ],
    "At Risk": [
        "❤️ {name}, we miss you! It's been a while. Here's a personal {discount}% discount — come back and let's reconnect.",
        "😔 We haven't seen you in a while, {name}. Life gets busy, we get it. Take {discount}% off, just because we care.",
        "🙏 {name}, your absence hasn't gone unnoticed. We'd love to have you back — enjoy {discount}% off on everything today.",
    ],
    "Cant Lose Them": [
        "🆘 {name}, please don't go! You're one of our most valued customers ever. Here's an exclusive {discount}% win-back offer + a surprise gift.",
        "💌 {name}, we value you deeply. Here's our biggest ever offer — {discount}% off + free shipping — because you deserve the best.",
        "🔑 {name}, unlock your ultimate comeback offer: {discount}% off + VIP status restored. We'd be honoured to have you back.",
    ],
    "Hibernating": [
        "😴 {name}, time to wake up! We have exciting new products + {discount}% off waiting for you — don't let it slip away.",
        "🌅 Hey {name}! It's a new season and new deals. Come see what you've been missing + save {discount}% on your return.",
        "🎁 {name}, consider this a friendly nudge! Here's {discount}% off to re-explore our store — we've added so much since your last visit.",
    ],
    "Lost": [
        "💫 {name}, we're reaching out one last time. Enjoy {discount}% off — our biggest discount ever — because we truly want you back.",
        "🌈 {name}, long time no see! We've completely refreshed our catalogue. Come explore + claim your exclusive {discount}% return offer.",
        "✉️ Dear {name}, we haven't forgotten you. Take {discount}% off your next order — no strings attached. We'd love to see you again.",
    ],
}

DISCOUNT_BY_SEGMENT = {
    "Champions":           10,
    "Loyal Customers":     15,
    "Recent Customers":    20,
    "Potential Loyalists": 18,
    "Promising":           20,
    "Needs Attention":     22,
    "At Risk":             25,
    "Cant Lose Them":      30,
    "Hibernating":         25,
    "Lost":                35,
}


def generate_campaign(
    segment: str,
    customer_name: str = "Valued Customer",
    churn_risk: float = 0.0,
    variant: Optional[int] = None,
) -> Dict:
    """
    Generates a personalized marketing campaign message.

    Args:
        segment: Customer segment label
        customer_name: Customer display name
        churn_risk: Churn probability (0-1)
        variant: Template index (random if None)

    Returns:
        dict with keys: message, discount, subject, urgency, channel
    """
    templates = CAMPAIGN_TEMPLATES.get(segment, CAMPAIGN_TEMPLATES["Hibernating"])
    discount  = DISCOUNT_BY_SEGMENT.get(segment, 20)

    # Boost discount if high churn risk
    if churn_risk >= 0.7:
        discount = min(discount + 5, 50)

    if variant is None:
        template = random.choice(templates)
    else:
        template = templates[variant % len(templates)]

    message = template.format(name=customer_name, discount=discount)

    # Derive subject line and channel
    meta    = get_segment_meta(segment)
    urgency = "🔥 Urgent" if churn_risk >= 0.7 else ("⏳ Time-Sensitive" if churn_risk >= 0.4 else "✨ Personalised")
    channel = _recommend_channel(segment, churn_risk)

    subject = _generate_subject(segment, customer_name, discount)

    return {
        "message":  message,
        "discount": discount,
        "subject":  subject,
        "urgency":  urgency,
        "channel":  channel,
        "segment":  segment,
        "emoji":    meta.get("emoji", "📧"),
    }


def _generate_subject(segment: str, name: str, discount: int) -> str:
    subjects = {
        "Champions":           f"👑 Your Exclusive VIP Reward is Here, {name}!",
        "Loyal Customers":     f"💚 A Special Thank-You Gift: {discount}% Off Just for You",
        "Recent Customers":    f"🌱 Welcome Back! {discount}% Off Your Next Visit",
        "Potential Loyalists": f"⭐ Unlock VIP Status — {discount}% Off Inside",
        "Promising":           f"🌟 {name}, Here's Your Welcome Bonus: {discount}% Off",
        "Needs Attention":     f"⚡ Limited Offer: {discount}% Off Expires Soon, {name}",
        "At Risk":             f"❤️ We Miss You, {name} — {discount}% Off to Come Back",
        "Cant Lose Them":      f"🆘 {name}, Your Exclusive Win-Back Offer: {discount}% Off",
        "Hibernating":         f"😴 Time to Wake Up! {discount}% Off Waiting for You",
        "Lost":                f"💌 One Last Offer, {name}: {discount}% Off — We Miss You",
    }
    return subjects.get(segment, f"📧 A Special Offer Just for You — {discount}% Off")


def _recommend_channel(segment: str, churn_risk: float) -> str:
    high_risk = {"At Risk", "Cant Lose Them", "Lost"}
    if segment in high_risk or churn_risk >= 0.7:
        return "📱 SMS + 📧 Email + 🔔 Push Notification"
    elif segment in {"Champions", "Loyal Customers"}:
        return "📧 Email Newsletter + 📱 App Notification"
    else:
        return "📧 Email Campaign"


# ─────────────────────────────────────────────
# DECISION ENGINE
# ─────────────────────────────────────────────

def decision_engine(segment: str, churn_prob: float, monetary: float, frequency: int) -> Dict:
    """
    Combines segment + churn prediction to produce
    actionable business recommendations.
    """
    meta = get_segment_meta(segment)
    recommendations = []

    # Churn-based recommendations
    if churn_prob >= 0.8:
        recommendations.append("🚨 URGENT: High churn risk — trigger win-back sequence immediately.")
    elif churn_prob >= 0.5:
        recommendations.append("⚠️ Moderate churn risk — initiate re-engagement campaign within 7 days.")
    else:
        recommendations.append("✅ Low churn risk — focus on retention and upselling.")

    # Monetary-based
    if monetary >= 5000:
        recommendations.append("💰 High-value customer — assign dedicated account manager or VIP tier.")
    elif monetary >= 1000:
        recommendations.append("📈 Mid-tier spender — target with premium product recommendations.")
    else:
        recommendations.append("🛒 Low spender — introduce bundle deals and starter packages.")

    # Frequency-based
    if frequency >= 20:
        recommendations.append("🔁 Highly frequent buyer — enroll in subscription / loyalty program.")
    elif frequency >= 5:
        recommendations.append("🎯 Moderate buyer — send product discovery emails bi-weekly.")
    else:
        recommendations.append("📬 Low frequency — use educational content to build habit.")

    # Segment action
    recommendations.append(f"📌 Segment Strategy: {meta.get('action', 'Engage customer.')}")

    return {
        "segment":         segment,
        "priority":        meta.get("priority", "Medium"),
        "churn_risk_pct":  round(churn_prob * 100, 1),
        "recommendations": recommendations,
        "color":           meta.get("color", "#EDE9E3"),
    }


# ─────────────────────────────────────────────
# SUMMARY STATS HELPER
# ─────────────────────────────────────────────

def segment_summary(rfm_df) -> dict:
    """Returns per-segment aggregated statistics."""
    summary = (
        rfm_df.groupby("segment")
        .agg(
            customer_count = ("customer_id",  "count"),
            avg_recency    = ("recency",       "mean"),
            avg_frequency  = ("frequency",     "mean"),
            avg_monetary   = ("monetary",      "mean"),
            total_revenue  = ("monetary",      "sum"),
            churn_rate     = ("churn_predict", "mean") if "churn_predict" in rfm_df.columns else ("recency", lambda x: 0),
        )
        .round(2)
        .reset_index()
    )
    return summary
