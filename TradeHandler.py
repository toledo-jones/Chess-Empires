import random
import Constant


class TradeHandler:
    def __init__(self, engine):
        self.engine = engine
        self.resources = ('wood', 'gold', 'stone')
        self.give_upper_bound, self.give_lower_bound = Constant.TRADING_GIVE_BOUNDS[0], Constant.TRADING_GIVE_BOUNDS[1]
        self.receive_upper_bound, self.receive_lower_bound = Constant.TRADING_RECEIVE_BOUNDS[0], Constant.TRADING_RECEIVE_BOUNDS[1]

    def get_conversions(self):
        conversions = {}
        for resource in self.resources:
            conversions[resource] = (random.uniform(self.give_lower_bound, self.give_upper_bound), random.uniform(self.receive_lower_bound,self.give_upper_bound))
        return conversions

    def get_receive_conversion(self, give_amount, receive_resource):
        receive_rate = self.engine.trade_conversions[self.engine.turn_count_actual][receive_resource][1]
        receive_amount = round(give_amount * receive_rate)
        if receive_amount == 0:
            receive_amount = 1
        return receive_amount

    def get_give_conversion(self, give_resource, player):
        amount = getattr(player, give_resource)
        give_rate = self.engine.trade_conversions[self.engine.turn_count_actual][give_resource][0]
        give_amount = amount * give_rate
        return round(give_amount)
