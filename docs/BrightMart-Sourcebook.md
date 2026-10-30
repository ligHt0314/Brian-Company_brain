# BrightMart source book

All people, stores and records below are fictional. Generated from the exact imported source bodies.



## Easy Checkout · architecture

Record: doc:checkout-architecture · Access: engineering · Updated: 2026-10-14T04:00:00Z



Payment confirmation relies on confirmed bank payments. Dependency changes require a release review.

Easy Checkout uses Checkout Service.

Checkout Service depends on Payment Gateway.

Checkout Service has primary owner Payments.

Maya Rao worked on Checkout Service.

Leah Chen worked on Easy Checkout.



## Payment Gateway · operational runbook

Record: doc:payments-runbook · Access: engineering · Updated: 2026-08-20T04:00:00Z



Runbook from the previous operating cycle. Confirm ownership before paging a team.

Payment Gateway has primary owner Payments.

Maya Rao worked on Payment Gateway.



## Green Basket Stores · rollout commitment

Record: doc:green-basket-rollout · Access: engineering · Updated: 2026-10-14T04:00:00Z



The promised rollout includes payment confirmation. This is synthetic customer information.

C-101 requires Easy Checkout.

C-101 is made to Green Basket Stores.

C-101 is due on 2026-10-18.



## Easy Checkout · project brief

Record: doc:checkout-brief · Access: all_employees · Updated: 2026-10-14T04:00:00Z



Easy Checkout is our faster online checkout project. Alias: Checkout Launch. Its technical dependencies are documented in engineering records.

Leah Chen worked on Easy Checkout.



## Sales Dashboard · project overview

Record: doc:dashboard-overview · Access: all_employees · Updated: 2026-10-14T04:00:00Z



Sales Dashboard uses Reporting Service.

Reporting Service has primary owner Data Systems.

C-102 requires Sales Dashboard.

C-102 is made to Daily Essentials.

C-102 is due on 2026-10-30.



## Leadership · commercial planning

Record: doc:leadership-note · Access: leadership · Updated: 2026-10-14T04:00:00Z



CONFIDENTIAL_BRIGHTMART_COPPER_731. Fictional leadership-only commercial planning marker.

Easy Checkout has primary owner Leah Chen.



## Engineering handoff · Payment Gateway

Record: chat:handoff · Access: engineering · Updated: 2026-10-14T04:00:00Z



Exported conversation, 14 October. The earlier runbook has not been reconciled with this handoff claim.

Payment Gateway now has primary owner Integrations.

Dev Shah worked on Payment Gateway.



## Payment Gateway · implementation help

Record: chat:payments-help · Access: engineering · Updated: 2026-10-14T04:00:00Z



Maya and Dev shared their implementation experience. Contribution is not formal ownership.

Maya Rao worked on Payment Gateway.

Dev Shah worked on Payment Gateway.

Nina Park worked on Checkout Service.



## Checkout Launch · release planning

Record: chat:checkout-planning · Access: engineering · Updated: 2026-10-14T04:00:00Z



Planning discussion: investigate dependencies and the customer promise before release review.

Leah Chen worked on Easy Checkout.

Maya Rao worked on Easy Checkout.

Dev Shah worked on Checkout Service.



## Dashboard · planning notes

Record: chat:dashboard-planning · Access: all_employees · Updated: 2026-10-14T04:00:00Z



Omar Ali worked on Sales Dashboard.

Eli Morgan worked on Reporting Service.



## Shared Launch alias · naming discussion

Record: chat:ambiguous-alias · Access: all_employees · Updated: 2026-10-14T04:00:00Z



Both Easy Checkout and Sales Dashboard are sometimes called Launch. Ask which project is intended.







## T-101 · Payment confirmation check

Record: ticket:T-101 · Access: engineering · Updated: 2026-10-17T03:30:00Z



T-101 blocks Payment Gateway.

T-101 has status blocked.



## T-102 · Checkout smoke tests

Record: ticket:T-102 · Access: engineering · Updated: 2026-10-17T03:30:00Z



T-102 blocks Checkout Service.

T-102 has status done.



## T-103 · Analytics backfill

Record: ticket:T-103 · Access: all_employees · Updated: 2026-10-17T03:30:00Z



T-103 blocks Reporting Service.

T-103 has status open.



## T-104 · Notification delivery

Record: ticket:T-104 · Access: engineering · Updated: 2026-10-17T03:30:00Z



T-104 blocks Customer Messages.

T-104 has status in_progress.



## T-105 · Old payment cleanup

Record: ticket:T-105 · Access: engineering · Updated: 2026-10-17T03:30:00Z



T-105 blocks Payment Gateway.

T-105 has status cancelled.



## T-106 · Payment reconciliation review

Record: ticket:T-106 · Access: engineering · Updated: 2026-10-17T03:30:00Z



T-106 blocks Payment Gateway.

T-106 has status done.

Maya Rao worked on T-106.

Dev Shah worked on T-106.



## T-107 · Notification metrics

Record: ticket:T-107 · Access: engineering · Updated: 2026-10-17T03:30:00Z



T-107 blocks Customer Messages.

T-107 has status done.



## T-108 · Untriaged delivery check

Record: ticket:T-108 · Access: engineering · Updated: 2026-10-17T03:30:00Z



T-108 blocks Customer Messages.



## D-102 · Checkout payment validation

Record: decision:D-102 · Access: engineering · Updated: 2026-10-14T04:00:00Z



D-102 is about Checkout Service: validate payment reference before issuing a order confirmation.



## D-103 · Analytics backfill

Record: decision:D-103 · Access: all_employees · Updated: 2026-10-14T04:00:00Z



D-103 is about Sales Dashboard: complete the backfill before the analytics review.



## D-104 · Payment audit trail

Record: decision:D-104 · Access: engineering · Updated: 2026-06-01T04:00:00Z



D-104 is about Payment Gateway: keep a payment audit trail for operational investigation.



## D-101 · Confirm payment before accepting an order

Record: decision:D-101 · Access: engineering · Updated: 2026-10-16T04:00:00Z



D-101 is about Easy Checkout: unconfirmed payments are ruled out because Green Basket Stores requires confirmed payment before an order is accepted. This prevents shoppers seeing an order confirmation when the bank has not accepted the payment.



## Quick Refunds · plain-language project brief

Record: doc:quick-refunds-brief · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Return money promptly after an approved cancellation. This project is part of the fictional BrightMart demonstration.

Ananya Sen worked on Quick Refunds.



## Quick Refunds · delivery plan

Record: doc:quick-refunds-plan · Access: engineering · Updated: 2026-10-16T04:00:00Z



Business purpose: Return money promptly after an approved cancellation. The facts below show which systems the project needs.

Quick Refunds uses Refund Service.

Refund Service depends on Payment Gateway.



## Stock Alerts · plain-language project brief

Record: doc:stock-alerts-brief · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Warn stores before popular items run out. This project is part of the fictional BrightMart demonstration.

Kabir Khan worked on Stock Alerts.



## Stock Alerts · delivery plan

Record: doc:stock-alerts-plan · Access: engineering · Updated: 2026-10-16T04:00:00Z



Business purpose: Warn stores before popular items run out. The facts below show which systems the project needs.

Stock Alerts uses Stock Counter.

Stock Counter depends on Product Catalog.



## Store Pickup · plain-language project brief

Record: doc:store-pickup-brief · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Let shoppers collect their order from a store. This project is part of the fictional BrightMart demonstration.

Meera Nair worked on Store Pickup.



## Store Pickup · delivery plan

Record: doc:store-pickup-plan · Access: engineering · Updated: 2026-10-16T04:00:00Z



Business purpose: Let shoppers collect their order from a store. The facts below show which systems the project needs.

Store Pickup uses Pickup Scheduler.

Pickup Scheduler depends on Stock Counter.



## Customer Rewards · plain-language project brief

Record: doc:customer-rewards-brief · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Give repeat shoppers reward points. This project is part of the fictional BrightMart demonstration.

Arjun Iyer worked on Customer Rewards.



## Customer Rewards · delivery plan

Record: doc:customer-rewards-plan · Access: engineering · Updated: 2026-10-16T04:00:00Z



Business purpose: Give repeat shoppers reward points. The facts below show which systems the project needs.

Customer Rewards uses Rewards Wallet.

Rewards Wallet depends on Customer Messages.



## Seller Dashboard · plain-language project brief

Record: doc:seller-dashboard-brief · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Help partner stores manage their online business. This project is part of the fictional BrightMart demonstration.

Sara Thomas worked on Seller Dashboard.



## Seller Dashboard · delivery plan

Record: doc:seller-dashboard-plan · Access: engineering · Updated: 2026-10-16T04:00:00Z



Business purpose: Help partner stores manage their online business. The facts below show which systems the project needs.

Seller Dashboard uses Seller Portal.

Seller Portal depends on Product Catalog.



## Help Center · plain-language project brief

Record: doc:help-center-brief · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Help shoppers get an answer when something goes wrong. This project is part of the fictional BrightMart demonstration.

Vikram Joshi worked on Help Center.



## Help Center · delivery plan

Record: doc:help-center-plan · Access: engineering · Updated: 2026-10-16T04:00:00Z



Business purpose: Help shoppers get an answer when something goes wrong. The facts below show which systems the project needs.

Help Center uses Help Desk.

Help Desk depends on Customer Messages.



## Fresh Subscriptions · plain-language project brief

Record: doc:fresh-subscriptions-brief · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Let shoppers receive a regular grocery box. This project is part of the fictional BrightMart demonstration.

Diya Kapoor worked on Fresh Subscriptions.



## Fresh Subscriptions · delivery plan

Record: doc:fresh-subscriptions-plan · Access: engineering · Updated: 2026-10-16T04:00:00Z



Business purpose: Let shoppers receive a regular grocery box. The facts below show which systems the project needs.

Fresh Subscriptions uses Subscription Billing.

Subscription Billing depends on Payment Gateway.



## Delivery Board · working guide

Record: doc:delivery-board-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Delivery Board means the screen staff use to see where deliveries are. An owner is the team responsible for keeping this system working.

Delivery Board has primary owner Shopping Experience.

Delivery Board depends on Route Planner.



## Route Planner · working guide

Record: doc:route-planner-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Route Planner means the tool that chooses a delivery route. An owner is the team responsible for keeping this system working.

Route Planner has primary owner Customer Care.

Route Planner depends on Warehouse Updates.



## Refund Service · working guide

Record: doc:refunds-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Refund Service means the tool that returns money after an approved cancellation. An owner is the team responsible for keeping this system working.

Refund Service has primary owner Store Operations.

Refund Service depends on Payment Gateway.



## Stock Counter · working guide

Record: doc:inventory-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Stock Counter means the counter that tracks how many items are available. An owner is the team responsible for keeping this system working.

Stock Counter has primary owner Site Reliability.

Stock Counter depends on Product Catalog.



## Product Catalog · working guide

Record: doc:catalog-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Product Catalog means the list of products, prices and product details. An owner is the team responsible for keeping this system working.

Product Catalog has primary owner Payments.



## Rewards Wallet · working guide

Record: doc:loyalty-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Rewards Wallet means the balance of a shopper’s reward points. An owner is the team responsible for keeping this system working.

Rewards Wallet has primary owner Integrations.

Rewards Wallet depends on Customer Messages.



## Seller Portal · working guide

Record: doc:seller-portal-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Seller Portal means the workspace used by partner stores. An owner is the team responsible for keeping this system working.

Seller Portal has primary owner Data Systems.

Seller Portal depends on Product Catalog.



## Help Desk · working guide

Record: doc:support-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Help Desk means the workspace used to help shoppers. An owner is the team responsible for keeping this system working.

Help Desk has primary owner Delivery Operations.

Help Desk depends on Customer Messages.



## Subscription Billing · working guide

Record: doc:billing-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Subscription Billing means the tool that charges repeat grocery subscriptions. An owner is the team responsible for keeping this system working.

Subscription Billing has primary owner Shopping Experience.

Subscription Billing depends on Payment Gateway.



## Warehouse Updates · working guide

Record: doc:warehouse-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Warehouse Updates means the feed that reports packing and stock movements. An owner is the team responsible for keeping this system working.

Warehouse Updates has primary owner Customer Care.



## Pickup Scheduler · working guide

Record: doc:pickup-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Pickup Scheduler means the tool that reserves a collection time at a store. An owner is the team responsible for keeping this system working.

Pickup Scheduler has primary owner Store Operations.

Pickup Scheduler depends on Stock Counter.



## Product Search · working guide

Record: doc:search-runbook · Access: engineering · Updated: 2026-10-16T04:00:00Z



Product Search means the tool shoppers use to find products. An owner is the team responsible for keeping this system working.

Product Search has primary owner Site Reliability.

Product Search depends on Product Catalog.



## Checkout Service · weekly handover

Record: chat:checkout-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Arjun Iyer worked on Checkout Service.



## Payment Gateway · weekly handover

Record: chat:payments-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Sara Thomas worked on Payment Gateway.



## Reporting Service · weekly handover

Record: chat:reporting-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Vikram Joshi worked on Reporting Service.



## Customer Messages · weekly handover

Record: chat:messages-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Diya Kapoor worked on Customer Messages.



## Delivery Board · weekly handover

Record: chat:delivery-board-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Neel Gupta worked on Delivery Board.



## Route Planner · weekly handover

Record: chat:route-planner-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Tara Bose worked on Route Planner.



## Refund Service · weekly handover

Record: chat:refunds-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Aditya Rao worked on Refund Service.



## Stock Counter · weekly handover

Record: chat:inventory-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Zoya Malik worked on Stock Counter.



## Product Catalog · weekly handover

Record: chat:catalog-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Rehan Shah worked on Product Catalog.



## Rewards Wallet · weekly handover

Record: chat:loyalty-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Anika Jain worked on Rewards Wallet.



## Seller Portal · weekly handover

Record: chat:seller-portal-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Kiran Menon worked on Seller Portal.



## Help Desk · weekly handover

Record: chat:support-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Pooja Desai worked on Help Desk.



## Subscription Billing · weekly handover

Record: chat:billing-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Amit Verma worked on Subscription Billing.



## Warehouse Updates · weekly handover

Record: chat:warehouse-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Sana Sheikh worked on Warehouse Updates.



## Pickup Scheduler · weekly handover

Record: chat:pickup-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Raj Malhotra worked on Pickup Scheduler.



## Product Search · weekly handover

Record: chat:search-weekly · Access: engineering · Updated: 2026-10-16T04:00:00Z



Fictional exported team discussion. The people below contributed to this system; that alone does not make them its owner.

Nisha Reddy worked on Product Search.



## Maya Rao · contribution notes

Record: doc:work-maya · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Delivery Board is the screen staff use to see where deliveries are.

Maya Rao worked on Delivery Board.

Maya Rao worked on Delivery Tracking.



## Dev Shah · contribution notes

Record: doc:work-dev · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Route Planner is the tool that chooses a delivery route.

Dev Shah worked on Route Planner.

Dev Shah worked on Quick Refunds.



## Leah Chen · contribution notes

Record: doc:work-leah · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Refund Service is the tool that returns money after an approved cancellation.

Leah Chen worked on Refund Service.

Leah Chen worked on Stock Alerts.



## Omar Ali · contribution notes

Record: doc:work-omar · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Stock Counter is the counter that tracks how many items are available.

Omar Ali worked on Stock Counter.

Omar Ali worked on Store Pickup.



## Nina Park · contribution notes

Record: doc:work-nina · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Product Catalog is the list of products, prices and product details.

Nina Park worked on Product Catalog.

Nina Park worked on Customer Rewards.



## Eli Morgan · contribution notes

Record: doc:work-eli · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Rewards Wallet is the balance of a shopper’s reward points.

Eli Morgan worked on Rewards Wallet.

Eli Morgan worked on Seller Dashboard.



## Aarav Mehta · contribution notes

Record: doc:work-aarav-mehta · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Seller Portal is the workspace used by partner stores.

Aarav Mehta worked on Seller Portal.

Aarav Mehta worked on Help Center.



## Isha Patel · contribution notes

Record: doc:work-isha-patel · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Help Desk is the workspace used to help shoppers.

Isha Patel worked on Help Desk.

Isha Patel worked on Fresh Subscriptions.



## Rohan Das · contribution notes

Record: doc:work-rohan-das · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Subscription Billing is the tool that charges repeat grocery subscriptions.

Rohan Das worked on Subscription Billing.

Rohan Das worked on Delivery Tracking.



## Ananya Sen · contribution notes

Record: doc:work-ananya-sen · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Warehouse Updates is the feed that reports packing and stock movements.

Ananya Sen worked on Warehouse Updates.

Ananya Sen worked on Quick Refunds.



## Kabir Khan · contribution notes

Record: doc:work-kabir-khan · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Pickup Scheduler is the tool that reserves a collection time at a store.

Kabir Khan worked on Pickup Scheduler.

Kabir Khan worked on Stock Alerts.



## Meera Nair · contribution notes

Record: doc:work-meera-nair · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Product Search is the tool shoppers use to find products.

Meera Nair worked on Product Search.

Meera Nair worked on Store Pickup.



## Arjun Iyer · contribution notes

Record: doc:work-arjun-iyer · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Delivery Board is the screen staff use to see where deliveries are.

Arjun Iyer worked on Delivery Board.

Arjun Iyer worked on Customer Rewards.



## Sara Thomas · contribution notes

Record: doc:work-sara-thomas · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Route Planner is the tool that chooses a delivery route.

Sara Thomas worked on Route Planner.

Sara Thomas worked on Seller Dashboard.



## Vikram Joshi · contribution notes

Record: doc:work-vikram-joshi · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Refund Service is the tool that returns money after an approved cancellation.

Vikram Joshi worked on Refund Service.

Vikram Joshi worked on Help Center.



## Diya Kapoor · contribution notes

Record: doc:work-diya-kapoor · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Stock Counter is the counter that tracks how many items are available.

Diya Kapoor worked on Stock Counter.

Diya Kapoor worked on Fresh Subscriptions.



## Neel Gupta · contribution notes

Record: doc:work-neel-gupta · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Product Catalog is the list of products, prices and product details.

Neel Gupta worked on Product Catalog.

Neel Gupta worked on Delivery Tracking.



## Tara Bose · contribution notes

Record: doc:work-tara-bose · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Rewards Wallet is the balance of a shopper’s reward points.

Tara Bose worked on Rewards Wallet.

Tara Bose worked on Quick Refunds.



## Aditya Rao · contribution notes

Record: doc:work-aditya-rao · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Seller Portal is the workspace used by partner stores.

Aditya Rao worked on Seller Portal.

Aditya Rao worked on Stock Alerts.



## Zoya Malik · contribution notes

Record: doc:work-zoya-malik · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Help Desk is the workspace used to help shoppers.

Zoya Malik worked on Help Desk.

Zoya Malik worked on Store Pickup.



## Rehan Shah · contribution notes

Record: doc:work-rehan-shah · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Subscription Billing is the tool that charges repeat grocery subscriptions.

Rehan Shah worked on Subscription Billing.

Rehan Shah worked on Customer Rewards.



## Anika Jain · contribution notes

Record: doc:work-anika-jain · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Warehouse Updates is the feed that reports packing and stock movements.

Anika Jain worked on Warehouse Updates.

Anika Jain worked on Seller Dashboard.



## Kiran Menon · contribution notes

Record: doc:work-kiran-menon · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Pickup Scheduler is the tool that reserves a collection time at a store.

Kiran Menon worked on Pickup Scheduler.

Kiran Menon worked on Help Center.



## Pooja Desai · contribution notes

Record: doc:work-pooja-desai · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Product Search is the tool shoppers use to find products.

Pooja Desai worked on Product Search.

Pooja Desai worked on Fresh Subscriptions.



## Amit Verma · contribution notes

Record: doc:work-amit-verma · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Delivery Board is the screen staff use to see where deliveries are.

Amit Verma worked on Delivery Board.

Amit Verma worked on Delivery Tracking.



## Sana Sheikh · contribution notes

Record: doc:work-sana-sheikh · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Route Planner is the tool that chooses a delivery route.

Sana Sheikh worked on Route Planner.

Sana Sheikh worked on Quick Refunds.



## Raj Malhotra · contribution notes

Record: doc:work-raj-malhotra · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Refund Service is the tool that returns money after an approved cancellation.

Raj Malhotra worked on Refund Service.

Raj Malhotra worked on Stock Alerts.



## Nisha Reddy · contribution notes

Record: doc:work-nisha-reddy · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Stock Counter is the counter that tracks how many items are available.

Nisha Reddy worked on Stock Counter.

Nisha Reddy worked on Store Pickup.



## Varun Sethi · contribution notes

Record: doc:work-varun-sethi · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Product Catalog is the list of products, prices and product details.

Varun Sethi worked on Product Catalog.

Varun Sethi worked on Customer Rewards.



## Riya Bhat · contribution notes

Record: doc:work-riya-bhat · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Rewards Wallet is the balance of a shopper’s reward points.

Riya Bhat worked on Rewards Wallet.

Riya Bhat worked on Seller Dashboard.



## Yash Kulkarni · contribution notes

Record: doc:work-yash-kulkarni · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Seller Portal is the workspace used by partner stores.

Yash Kulkarni worked on Seller Portal.

Yash Kulkarni worked on Help Center.



## Aditi Roy · contribution notes

Record: doc:work-aditi-roy · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Help Desk is the workspace used to help shoppers.

Aditi Roy worked on Help Desk.

Aditi Roy worked on Fresh Subscriptions.



## Manav Suri · contribution notes

Record: doc:work-manav-suri · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Subscription Billing is the tool that charges repeat grocery subscriptions.

Manav Suri worked on Subscription Billing.

Manav Suri worked on Delivery Tracking.



## Simran Kaur · contribution notes

Record: doc:work-simran-kaur · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Warehouse Updates is the feed that reports packing and stock movements.

Simran Kaur worked on Warehouse Updates.

Simran Kaur worked on Quick Refunds.



## Siddharth Pai · contribution notes

Record: doc:work-siddharth-pai · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Pickup Scheduler is the tool that reserves a collection time at a store.

Siddharth Pai worked on Pickup Scheduler.

Siddharth Pai worked on Stock Alerts.



## Kavya Rao · contribution notes

Record: doc:work-kavya-rao · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Product Search is the tool shoppers use to find products.

Kavya Rao worked on Product Search.

Kavya Rao worked on Store Pickup.



## Ibrahim Noor · contribution notes

Record: doc:work-ibrahim-noor · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Delivery Board is the screen staff use to see where deliveries are.

Ibrahim Noor worked on Delivery Board.

Ibrahim Noor worked on Customer Rewards.



## Priya Dutta · contribution notes

Record: doc:work-priya-dutta · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Route Planner is the tool that chooses a delivery route.

Priya Dutta worked on Route Planner.

Priya Dutta worked on Seller Dashboard.



## Harsh Arora · contribution notes

Record: doc:work-harsh-arora · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Refund Service is the tool that returns money after an approved cancellation.

Harsh Arora worked on Refund Service.

Harsh Arora worked on Help Center.



## Lina Fernandes · contribution notes

Record: doc:work-lina-fernandes · Access: engineering · Updated: 2026-10-16T04:00:00Z



A record of work performed, not a claim about seniority, availability or ownership. Stock Counter is the counter that tracks how many items are available.

Lina Fernandes worked on Stock Counter.

Lina Fernandes worked on Fresh Subscriptions.



## T-109 · Delivery location stops updating (check 1)

Record: ticket:T-109 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-109 blocks Delivery Board.

T-109 has status blocked.

Aarav Mehta worked on T-109.



## T-110 · Refund reference missing from bank response (check 1)

Record: ticket:T-110 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-110 blocks Refund Service.

T-110 has status open.

Isha Patel worked on T-110.



## T-111 · Item quantity differs from store count (check 1)

Record: ticket:T-111 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-111 blocks Stock Counter.

T-111 has status in_progress.

Rohan Das worked on T-111.



## T-112 · Collection slot can be double-booked (check 1)

Record: ticket:T-112 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-112 blocks Pickup Scheduler.

T-112 has status done.

Ananya Sen worked on T-112.



## T-113 · Reward points applied twice (check 1)

Record: ticket:T-113 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-113 blocks Rewards Wallet.

T-113 has status done.

Kabir Khan worked on T-113.



## T-114 · Product price update arrives late (check 1)

Record: ticket:T-114 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-114 blocks Seller Portal.

T-114 has status cancelled.

Meera Nair worked on T-114.



## T-115 · Help request not assigned (check 1)

Record: ticket:T-115 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-115 blocks Help Desk.

T-115 has status done.

Arjun Iyer worked on T-115.



## T-116 · Repeat order charges fail (check 1)

Record: ticket:T-116 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-116 blocks Subscription Billing.

T-116 has status open.

Sara Thomas worked on T-116.



## T-117 · Route uses an unavailable road (check 1)

Record: ticket:T-117 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-117 blocks Route Planner.

T-117 has status done.

Vikram Joshi worked on T-117.



## T-118 · Packing update arrives out of order (check 1)

Record: ticket:T-118 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-118 blocks Warehouse Updates.

T-118 has status done.

Diya Kapoor worked on T-118.



## T-119 · Product search misses common names (check 1)

Record: ticket:T-119 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-119 blocks Product Search.

T-119 has status in_progress.

Neel Gupta worked on T-119.



## T-120 · Order text message arrives late (check 1)

Record: ticket:T-120 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-120 blocks Customer Messages.

T-120 has status done.

Tara Bose worked on T-120.



## T-121 · Delivery location stops updating (check 2)

Record: ticket:T-121 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-121 blocks Delivery Board.

T-121 has status blocked.

Aditya Rao worked on T-121.



## T-122 · Refund reference missing from bank response (check 2)

Record: ticket:T-122 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-122 blocks Refund Service.

T-122 has status open.

Zoya Malik worked on T-122.



## T-123 · Item quantity differs from store count (check 2)

Record: ticket:T-123 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-123 blocks Stock Counter.

T-123 has status in_progress.

Rehan Shah worked on T-123.



## T-124 · Collection slot can be double-booked (check 2)

Record: ticket:T-124 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-124 blocks Pickup Scheduler.

T-124 has status done.

Anika Jain worked on T-124.



## T-125 · Reward points applied twice (check 2)

Record: ticket:T-125 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-125 blocks Rewards Wallet.

T-125 has status done.

Kiran Menon worked on T-125.



## T-126 · Product price update arrives late (check 2)

Record: ticket:T-126 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-126 blocks Seller Portal.

T-126 has status cancelled.

Pooja Desai worked on T-126.



## T-127 · Help request not assigned (check 2)

Record: ticket:T-127 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-127 blocks Help Desk.

T-127 has status done.

Amit Verma worked on T-127.



## T-128 · Repeat order charges fail (check 2)

Record: ticket:T-128 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-128 blocks Subscription Billing.

T-128 has status open.

Sana Sheikh worked on T-128.



## T-129 · Route uses an unavailable road (check 2)

Record: ticket:T-129 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-129 blocks Route Planner.

T-129 has status done.

Raj Malhotra worked on T-129.



## T-130 · Packing update arrives out of order (check 2)

Record: ticket:T-130 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-130 blocks Warehouse Updates.

T-130 has status done.

Nisha Reddy worked on T-130.



## T-131 · Product search misses common names (check 2)

Record: ticket:T-131 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-131 blocks Product Search.

T-131 has status in_progress.

Varun Sethi worked on T-131.



## T-132 · Order text message arrives late (check 2)

Record: ticket:T-132 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-132 blocks Customer Messages.

T-132 has status done.

Riya Bhat worked on T-132.



## T-133 · Delivery location stops updating (check 3)

Record: ticket:T-133 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-133 blocks Delivery Board.

T-133 has status blocked.

Yash Kulkarni worked on T-133.



## T-134 · Refund reference missing from bank response (check 3)

Record: ticket:T-134 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-134 blocks Refund Service.

T-134 has status open.

Aditi Roy worked on T-134.



## T-135 · Item quantity differs from store count (check 3)

Record: ticket:T-135 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-135 blocks Stock Counter.

T-135 has status in_progress.

Manav Suri worked on T-135.



## T-136 · Collection slot can be double-booked (check 3)

Record: ticket:T-136 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-136 blocks Pickup Scheduler.

T-136 has status done.

Simran Kaur worked on T-136.



## T-137 · Reward points applied twice (check 3)

Record: ticket:T-137 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-137 blocks Rewards Wallet.

T-137 has status done.

Siddharth Pai worked on T-137.



## T-138 · Product price update arrives late (check 3)

Record: ticket:T-138 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-138 blocks Seller Portal.

T-138 has status cancelled.

Kavya Rao worked on T-138.



## T-139 · Help request not assigned (check 3)

Record: ticket:T-139 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-139 blocks Help Desk.

T-139 has status done.

Ibrahim Noor worked on T-139.



## T-140 · Repeat order charges fail (check 3)

Record: ticket:T-140 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-140 blocks Subscription Billing.

T-140 has status open.

Priya Dutta worked on T-140.



## T-141 · Route uses an unavailable road (check 3)

Record: ticket:T-141 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-141 blocks Route Planner.

T-141 has status done.

Harsh Arora worked on T-141.



## T-142 · Packing update arrives out of order (check 3)

Record: ticket:T-142 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-142 blocks Warehouse Updates.

T-142 has status done.

Lina Fernandes worked on T-142.



## T-143 · Product search misses common names (check 3)

Record: ticket:T-143 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-143 blocks Product Search.

T-143 has status in_progress.

Maya Rao worked on T-143.



## T-144 · Order text message arrives late (check 3)

Record: ticket:T-144 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-144 blocks Customer Messages.

T-144 has status done.

Dev Shah worked on T-144.



## T-145 · Delivery location stops updating (check 4)

Record: ticket:T-145 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-145 blocks Delivery Board.

T-145 has status blocked.

Leah Chen worked on T-145.



## T-146 · Refund reference missing from bank response (check 4)

Record: ticket:T-146 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-146 blocks Refund Service.

T-146 has status open.

Omar Ali worked on T-146.



## T-147 · Item quantity differs from store count (check 4)

Record: ticket:T-147 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-147 blocks Stock Counter.

T-147 has status in_progress.

Nina Park worked on T-147.



## T-148 · Collection slot can be double-booked (check 4)

Record: ticket:T-148 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-148 blocks Pickup Scheduler.

T-148 has status done.

Eli Morgan worked on T-148.



## T-149 · Reward points applied twice (check 4)

Record: ticket:T-149 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-149 blocks Rewards Wallet.

T-149 has status done.

Aarav Mehta worked on T-149.



## T-150 · Product price update arrives late (check 4)

Record: ticket:T-150 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-150 blocks Seller Portal.

T-150 has status cancelled.

Isha Patel worked on T-150.



## T-151 · Help request not assigned (check 4)

Record: ticket:T-151 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-151 blocks Help Desk.

T-151 has status done.

Rohan Das worked on T-151.



## T-152 · Repeat order charges fail (check 4)

Record: ticket:T-152 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-152 blocks Subscription Billing.

T-152 has status open.

Ananya Sen worked on T-152.



## T-153 · Route uses an unavailable road (check 4)

Record: ticket:T-153 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-153 blocks Route Planner.

T-153 has status done.

Kabir Khan worked on T-153.



## T-154 · Packing update arrives out of order (check 4)

Record: ticket:T-154 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-154 blocks Warehouse Updates.

T-154 has status done.

Meera Nair worked on T-154.



## T-155 · Product search misses common names (check 4)

Record: ticket:T-155 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-155 blocks Product Search.

T-155 has status in_progress.

Arjun Iyer worked on T-155.



## T-156 · Order text message arrives late (check 4)

Record: ticket:T-156 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-156 blocks Customer Messages.

T-156 has status done.

Sara Thomas worked on T-156.



## T-157 · Delivery location stops updating (check 5)

Record: ticket:T-157 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-157 blocks Delivery Board.

T-157 has status blocked.

Vikram Joshi worked on T-157.



## T-158 · Refund reference missing from bank response (check 5)

Record: ticket:T-158 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-158 blocks Refund Service.

T-158 has status open.

Diya Kapoor worked on T-158.



## T-159 · Item quantity differs from store count (check 5)

Record: ticket:T-159 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-159 blocks Stock Counter.

T-159 has status in_progress.

Neel Gupta worked on T-159.



## T-160 · Collection slot can be double-booked (check 5)

Record: ticket:T-160 · Access: engineering · Updated: 2026-10-17T03:30:00Z



A fictional work item. Status done or cancelled means it is not an active blocker; open, in_progress or blocked still needs attention.

T-160 blocks Pickup Scheduler.

T-160 has status done.

Tara Bose worked on T-160.



## D-105 · Show the last delivery update time

Record: decision:D-105 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-105 is about Delivery Tracking: show the last delivery update time so shoppers know when a location might be out of date.



## D-106 · Ask the bank for a refund reference

Record: decision:D-106 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-106 is about Quick Refunds: ask the bank for a refund reference so customer care can trace the money.



## D-107 · Check stock before taking a collection booking

Record: decision:D-107 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-107 is about Stock Alerts: check stock before taking a collection booking so stores do not promise an item that has sold out.



## D-108 · Use one reward entry per completed order

Record: decision:D-108 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-108 is about Store Pickup: use one reward entry per completed order so a retry cannot award the points twice.



## D-109 · Explain failed subscription payments

Record: decision:D-109 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-109 is about Customer Rewards: explain failed subscription payments so shoppers can fix payment details without placing duplicate orders.



## D-110 · Keep a history of changed product prices

Record: decision:D-110 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-110 is about Seller Dashboard: keep a history of changed product prices so stores can explain the price accepted for an order.



## D-111 · Send one notification per order event

Record: decision:D-111 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-111 is about Help Center: send one notification per order event so retries do not send shoppers the same message repeatedly.



## D-112 · Keep human review for disputed refunds

Record: decision:D-112 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-112 is about Fresh Subscriptions: keep human review for disputed refunds so a missing detail does not cause an automatic rejection.



## D-113 · Show the last delivery update time

Record: decision:D-113 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-113 is about Delivery Tracking: show the last delivery update time so shoppers know when a location might be out of date.



## D-114 · Ask the bank for a refund reference

Record: decision:D-114 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-114 is about Quick Refunds: ask the bank for a refund reference so customer care can trace the money.



## D-115 · Check stock before taking a collection booking

Record: decision:D-115 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-115 is about Stock Alerts: check stock before taking a collection booking so stores do not promise an item that has sold out.



## D-116 · Use one reward entry per completed order

Record: decision:D-116 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-116 is about Store Pickup: use one reward entry per completed order so a retry cannot award the points twice.



## D-117 · Explain failed subscription payments

Record: decision:D-117 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-117 is about Customer Rewards: explain failed subscription payments so shoppers can fix payment details without placing duplicate orders.



## D-118 · Keep a history of changed product prices

Record: decision:D-118 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-118 is about Seller Dashboard: keep a history of changed product prices so stores can explain the price accepted for an order.



## D-119 · Send one notification per order event

Record: decision:D-119 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-119 is about Help Center: send one notification per order event so retries do not send shoppers the same message repeatedly.



## D-120 · Keep human review for disputed refunds

Record: decision:D-120 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-120 is about Fresh Subscriptions: keep human review for disputed refunds so a missing detail does not cause an automatic rejection.



## D-121 · Show the last delivery update time

Record: decision:D-121 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-121 is about Delivery Tracking: show the last delivery update time so shoppers know when a location might be out of date.



## D-122 · Ask the bank for a refund reference

Record: decision:D-122 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-122 is about Quick Refunds: ask the bank for a refund reference so customer care can trace the money.



## D-123 · Check stock before taking a collection booking

Record: decision:D-123 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-123 is about Stock Alerts: check stock before taking a collection booking so stores do not promise an item that has sold out.



## D-124 · Use one reward entry per completed order

Record: decision:D-124 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional recorded product decision. The quotation explains the reason; it is not a claim that this policy applies to every project.

D-124 is about Store Pickup: use one reward entry per completed order so a retry cannot award the points twice.



## Daily Essentials · Sales Dashboard promise

Record: doc:promise-C-104 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-104 requires Sales Dashboard.

C-104 is made to Daily Essentials.

C-104 is due on 2026-10-20.



## Sunrise Supermarkets · Delivery Tracking promise

Record: doc:promise-C-105 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-105 requires Delivery Tracking.

C-105 is made to Sunrise Supermarkets.

C-105 is due on 2026-10-21.



## Family Pantry · Quick Refunds promise

Record: doc:promise-C-106 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-106 requires Quick Refunds.

C-106 is made to Family Pantry.

C-106 is due on 2026-10-22.



## City Corner Shops · Stock Alerts promise

Record: doc:promise-C-107 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-107 requires Stock Alerts.

C-107 is made to City Corner Shops.

C-107 is due on 2026-10-23.



## Fresh Farms Co-op · Store Pickup promise

Record: doc:promise-C-108 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-108 requires Store Pickup.

C-108 is made to Fresh Farms Co-op.

C-108 is due on 2026-10-24.



## Happy Home Grocers · Customer Rewards promise

Record: doc:promise-C-109 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-109 requires Customer Rewards.

C-109 is made to Happy Home Grocers.

C-109 is due on 2026-10-25.



## Neighbourhood Mart · Seller Dashboard promise

Record: doc:promise-C-110 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-110 requires Seller Dashboard.

C-110 is made to Neighbourhood Mart.

C-110 is due on 2026-10-26.



## Value Basket · Help Center promise

Record: doc:promise-C-111 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-111 requires Help Center.

C-111 is made to Value Basket.

C-111 is due on 2026-10-27.



## Organic Lane · Fresh Subscriptions promise

Record: doc:promise-C-112 · Access: engineering · Updated: 2026-10-16T04:00:00Z



A fictional customer promise: the project must be available before this rollout can be considered complete. A dependency risk is not proof the date will be missed.

C-112 requires Fresh Subscriptions.

C-112 is made to Organic Lane.

C-112 is due on 2026-10-28.



## Payments · team handbook

Record: doc:team-payments · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Payments works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Integrations · team handbook

Record: doc:team-integrations · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Integrations works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Data Systems · team handbook

Record: doc:team-data · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Data Systems works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Delivery Operations · team handbook

Record: doc:team-delivery · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Delivery Operations works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Shopping Experience · team handbook

Record: doc:team-shopping · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Shopping Experience works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Customer Care · team handbook

Record: doc:team-customer-care · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Customer Care works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Store Operations · team handbook

Record: doc:team-retail-ops · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Store Operations works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Site Reliability · team handbook

Record: doc:team-reliability · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart fictional team handbook. Site Reliability works with the other teams to support grocery shopping. The shared directory records actual team membership in this demonstration.



## Leadership · internal planning note 1

Record: doc:leadership-1 · Access: leadership · Updated: 2026-10-16T04:00:00Z



CONFIDENTIAL_BRIGHTMART_PRIVATE_1. Fictional leadership planning note, intentionally restricted for the permission demonstration. No real commercial information is present.





## Leadership · internal planning note 2

Record: doc:leadership-2 · Access: leadership · Updated: 2026-10-16T04:00:00Z



CONFIDENTIAL_BRIGHTMART_PRIVATE_2. Fictional leadership planning note, intentionally restricted for the permission demonstration. No real commercial information is present.





## Leadership · internal planning note 3

Record: doc:leadership-3 · Access: leadership · Updated: 2026-10-16T04:00:00Z



CONFIDENTIAL_BRIGHTMART_PRIVATE_3. Fictional leadership planning note, intentionally restricted for the permission demonstration. No real commercial information is present.





## Delivery Tracking · how the delivery chain works

Record: doc:delivery-story · Access: engineering · Updated: 2026-10-16T04:00:00Z



A shopper asks where the van is. Delivery Tracking uses the Delivery Board, which needs Route Planner information. Follow the evidence to see what a routing problem could affect.

Delivery Tracking uses Delivery Board.

Delivery Board depends on Route Planner.



## Start here · the BrightMart story

Record: doc:demo-welcome · Access: all_employees · Updated: 2026-10-16T04:00:00Z



BrightMart is a fictional online grocery retailer. Start with Easy Checkout: a payment confirmation check is blocked, two teams disagree about the Payment Gateway owner, and Green Basket Stores has a rollout promise. Other stories cover delivery tracking, refunds, stock, collection, rewards and reports. All people and records are invented. The demonstration guide explains the questions to ask; the agent answers from indexed evidence, not this guide.





## BrightMart · team directory

Record: directory:brightmart · Access: all_employees · Updated: 2026-10-16T04:00:00Z



Forty invented employees help ten fictional grocery-store customers sell online. Team membership identifies colleagues, not service ownership.

Maya Rao is a member of Payments.

Dev Shah is a member of Integrations.

Leah Chen is a member of Payments.

Omar Ali is a member of Data Systems.

Nina Park is a member of Integrations.

Eli Morgan is a member of Data Systems.

Aarav Mehta is a member of Store Operations.

Isha Patel is a member of Site Reliability.

Rohan Das is a member of Payments.

Ananya Sen is a member of Integrations.

Kabir Khan is a member of Data Systems.

Meera Nair is a member of Delivery Operations.

Arjun Iyer is a member of Shopping Experience.

Sara Thomas is a member of Customer Care.

Vikram Joshi is a member of Store Operations.

Diya Kapoor is a member of Site Reliability.

Neel Gupta is a member of Payments.

Tara Bose is a member of Integrations.

Aditya Rao is a member of Data Systems.

Zoya Malik is a member of Delivery Operations.

Rehan Shah is a member of Shopping Experience.

Anika Jain is a member of Customer Care.

Kiran Menon is a member of Store Operations.

Pooja Desai is a member of Site Reliability.

Amit Verma is a member of Payments.

Sana Sheikh is a member of Integrations.

Raj Malhotra is a member of Data Systems.

Nisha Reddy is a member of Delivery Operations.

Varun Sethi is a member of Shopping Experience.

Riya Bhat is a member of Customer Care.

Yash Kulkarni is a member of Store Operations.

Aditi Roy is a member of Site Reliability.

Manav Suri is a member of Payments.

Simran Kaur is a member of Integrations.

Siddharth Pai is a member of Data Systems.

Kavya Rao is a member of Delivery Operations.

Ibrahim Noor is a member of Shopping Experience.

Priya Dutta is a member of Customer Care.

Harsh Arora is a member of Store Operations.

Lina Fernandes is a member of Site Reliability.


