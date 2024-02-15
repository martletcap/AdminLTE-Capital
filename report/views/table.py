from home.models import MoneyTransaction, ShareTransaction

def extended_transaction_table(company):
    res = []
    money_transactions = MoneyTransaction.objects.filter(
        company = company
    ).order_by('date')
    for money_transaction in money_transactions:
        price = money_transaction.price
        transaction_type = money_transaction.transaction_type
        portfolio = money_transaction.portfolio
        share_transactions = ShareTransaction.objects.filter(
            money_transaction = money_transaction
        ).order_by('date')
        # Calculate cost per share
        cost_per_share = 0
        total_amount = 0
        for share_transaction in share_transactions:
            total_amount += share_transaction.amount
        if total_amount:
            cost_per_share = price/total_amount

        if len(share_transactions)==0:
            res.append([
                money_transaction.date, price, 0, cost_per_share,
                transaction_type, '', portfolio, money_transaction.comment,
            ])
        elif (len(share_transactions)==1 and 
              share_transactions[0].date == money_transaction.date):
            share_transaction = share_transactions[0]
            amount = share_transaction.amount
            share_type = share_transaction.share.type
            comment = f'{money_transaction.company} | {share_transaction.comment}'
            res.append([
                money_transaction.date, price, amount, cost_per_share,
                transaction_type, share_type, portfolio, comment,
            ])
        else:
            res.append([
                money_transaction.date, price, 0, 0, transaction_type,
                '', portfolio, money_transaction.comment
            ])
            for share_transaction in share_transactions:
                amount = share_transaction.amount
                share_type = share_transaction.share.type
                res.append([
                    share_transaction.date, 0, amount, cost_per_share,
                    '', share_type, '', share_transaction.comment
                ])
    return res