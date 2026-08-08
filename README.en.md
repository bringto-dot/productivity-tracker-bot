# Productivity Tracker Bot

**Language:** 🇷🇺 [Русский](README.md) · 🇬🇧 [English](README.en.md)

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![aiogram](https://img.shields.io/badge/aiogram-3-2CA5E0)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20async-D71F00)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC)
![License](https://img.shields.io/badge/license-MIT-green)

A Telegram productivity tracker designed as a complete product inside Telegram.

The project combines daily check-ins, progress tracking, statistics, premium
content, subscriptions, Telegram Stars payments, referrals, reminders and an
administrative interface in one system.

> This repository contains a demonstration version with test data and demo
> content. The core architecture and product mechanics are designed to be
> adapted to a specific product, niche and brand.

---

## Overview

The main user flow is built around a daily check-in.

Users rate their day from 1 to 10 and can optionally add a short note. The
bot stores the result and uses the accumulated history to build a personal
progress overview.

The Telegram interface includes:

- daily check-ins
- current and best streaks
- 7-day and 30-day statistics
- check-in history
- a categorized PDF library
- premium subscriptions
- a referral system
- automated reminders
- Russian and English localization

The complete user experience is handled inside Telegram without a separate
web application.

---

## Productivity Tracking

The core mechanic focuses on consistency rather than isolated daily scores.

Each completed check-in updates the user's history and allows the system to
calculate current and best streaks, averages and period-based statistics.

The tracking logic is separated from the Telegram handlers, keeping the
business rules independent from the interface.

The same structure can also be adapted to other recurring activities such as
workouts, learning or habit tracking.

---

## Content & Premium Access

The bot includes a categorized library of PDF materials.

Content can be divided between free and premium access, with subscription
status determining which materials are available to the user.

Content and subscription settings are connected to the administrative layer,
allowing the product to be managed without changing the user-facing
interface.

This makes the bot more than a simple tracker: the same system can support a
subscription-based content product.

---

## Subscriptions & Telegram Stars

Premium access is monetized directly through Telegram Stars.

The user selects a subscription plan inside the bot and proceeds through
Telegram's payment flow:

```text
send_invoice
      ↓
pre_checkout_query
      ↓
successful_payment
```

The project supports multiple plans, with their parameters stored in the
database and managed through the administrative interface.

The entire purchase flow remains inside Telegram.

## Referral System

Each user receives a personal referral link.

When a new user joins through that link, the system associates the referral
with its owner and tracks the required conversion event.

In the current implementation, a successful referral grants additional
premium days.

The referral logic is isolated in a dedicated service rather than being
placed directly inside the Telegram handlers.

## Administration

The project includes a dedicated admin interface that also runs inside
Telegram.

Administrators can:

- monitor DAU, WAU and MAU
- track revenue and conversion
- manage users
- grant or revoke premium access
- block users
- create and edit content
- manage subscription plans
- send broadcasts

No separate web dashboard is required for these operations.

This allows Telegram to serve as both the customer-facing interface and the
internal product management environment.

## Automation

Recurring tasks are handled by a scheduler.

The bot checks which users have not completed their daily check-in and can
automatically send them reminders.

This keeps the daily workflow running without requiring manual intervention
from an administrator.

## Localization

The interface supports both Russian and English.

Localization is kept separate from the main application logic, which makes
interface copy easier to maintain and allows additional languages to be
introduced without rewriting the core user flows.

## Architecture

The project is organized into separate layers for the main areas of
responsibility:

```
bot/
├── database/       # database models and data access
├── handlers/       # user and admin flows
├── keyboards/      # Telegram interface
├── middlewares/    # database sessions and user context
├── services/       # business logic
├── locales/        # RU / EN localization
├── states/         # conversation states
├── config.py       # configuration
└── main.py         # application entry point

sample_guides/      # demo PDF materials
scripts/            # utility scripts
tests/              # automated tests
```

Business logic for payments, referrals, tracking and other product
mechanics is separated from the Telegram handlers.

This keeps the interface layer focused on user interaction while the
underlying services handle the actual product logic.

## Testing

Key business logic is covered by automated tests.

The test suite includes checks for:

- streak calculation
- referral rewards
- RU / EN translation consistency
- subscription extension logic

The project uses `pytest` for testing.

## Deployment

The project is prepared for deployment both directly on a server and through
Docker.

The bot uses long polling, so the Telegram application itself does not
require a separate domain or SSL certificate.

The repository includes Docker configuration and separate deployment
documentation.

## Technology

### Backend

- Python 3.11+
- aiogram 3
- SQLAlchemy 2.0 Async
- SQLite
- Pydantic Settings

### Product

- Telegram Stars
- APScheduler
- subscription system
- referral system
- bilingual interface
- PDF content library

### Infrastructure

- Docker
- Docker Compose
- pytest

## Project Result

The result is a complete Telegram-based product rather than a collection of
isolated bot commands.

The project brings together the user experience, tracking logic, content,
monetization, referrals, automation and administration into one system.

The architecture can be adapted to another niche by changing the branding,
content, core metric, subscription model and user flows.
