import numpy as np
import pandas as pd
import time
import os
from sko.GA import GA
from sko.PSO import PSO
from multiprocessing import Process
from .ampo.ampo import AMPO


class Optimizer:
    def __init__(self):
        self.pop = 50
        self.iterations = 1000

    def runOptimizer(self, stocks, algo, allowShort, pop, iterations):
        self.pop = pop
        self.iterations = iterations
        self.portfolioData = {}
        if allowShort:
            bound = [-1,1]
        else:
            bound = [0,1]
        self.problem_size = len(stocks)
        stocks_num = self.problem_size
        stock_counter = 1
        mean_daily_returns = []
        cov_input = []
        for key, values in stocks.items():
            daily_returns = np.array(stocks[key])
            avg_return = daily_returns.mean()
            mean_daily_returns.append(avg_return)
            cov_input.append(daily_returns)
            stock_counter += 1
        mean_daily_returns = np.matrix(mean_daily_returns)
        cov_input = np.matrix(cov_input)
        cov_matrix = np.cov(cov_input)
        self.portfolioData[str(self.problem_size)] = [mean_daily_returns,cov_matrix]
        func = {'func_name': 'portfolio_func', 'func': self.portfolio_func, 'bound': bound}
        task = {'func': func, 'algo': algo, 'problem_size': self.problem_size}
        return self.run_process(0,task)

    def portfolio_func(self, weights):
        mean_daily_returns, cov_matrix = self.portfolioData[str(self.problem_size)]
        weights = np.abs(weights)
        weights = weights / np.abs(weights).sum()
        weights = np.matrix(weights)
        port_return = np.round(np.sum(weights * mean_daily_returns.T) * 2769, 2)/5 # 2769 trading days over 10 year period
        port_std_dev = np.round(np.sqrt(weights * cov_matrix * weights.T) * np.sqrt(2769), 2)/np.sqrt(5)
        port_std_dev = float(port_std_dev)
        sharpe_ratio = (port_return - 2.7)/ port_std_dev # 2.57 represents annual return of risk free security - 10-year US Treasury
        if sharpe_ratio <= 0:
            sharpe_ratio = 1E-10
        return  1.0/sharpe_ratio

    def run_process(self, process_no,task):
        # , 'GA': GA, 'PSO': PSO
        algo_dicts = {'AMPO': AMPO, 'GA': GA, 'PSO': PSO}
        res = []
        run_times = 1
        pop = self.pop
        iterations = self.iterations

        problem_size = task['problem_size']
        name = task['algo']

        Algo = algo_dicts[task['algo']]
        func = task['func']['func']
        func_name = task['func']['func_name']
        bound = task['func']['bound']
        fit_list = []
        cpu_times_list = []
        run_times_list = []

        for time_no in range(run_times):
            root_paras = {
                "problem_size": problem_size,
                "domain_range": bound,
                "print_train": False,
                "objective_func": func
                }

            start_processing_time = time.process_time()
            start_pref_time = time.perf_counter()

            if name == 'GA':
                algo = Algo(func = func, n_dim=problem_size, size_pop=pop, max_iter=iterations,
                        lb= (np.zeros(problem_size) + bound[0]).tolist(), ub=(np.zeros(problem_size) + bound[1]).tolist(), precision=1e-7)
                best_solution, best_fit = algo.run()
                best_fit = best_fit[0]
                raw_fit_history = algo.all_history_Y
                raw_fit_history = np.array(raw_fit_history).min(axis=1)
                cur_min = raw_fit_history[0]
                fit_history = []
                for cur_raw_fit in raw_fit_history:
                    if cur_raw_fit > cur_min:
                        fit_history.append(cur_min)
                    else:
                        cur_min = cur_raw_fit
                        fit_history.append(cur_raw_fit)
                fit_history = np.array(fit_history) # The history of the best fitness value. shape: (maxIterations, )

            elif name == 'PSO':
                algo = PSO(func=func, dim=problem_size, pop=pop, max_iter=iterations, lb= (np.zeros(problem_size) + bound[0]).tolist(), ub=(np.zeros(problem_size) + bound[1]).tolist(), w=0.8, c1=0.5, c2=0.5)
                best_solution, best_fit = algo.run(precision=None)
                fit_history = np.array(algo.gbest_y_hist)  # The history of the best fitness value. shape: (maxIterations, )
                fit_history = np.transpose(fit_history)[0]

            elif name == 'AMPO':
                algo = AMPO(func=func, dim=problem_size, bound=bound, pop=pop, max_iters=iterations, p_ld_ls=0.8, p_ls_ls=0.8, pr=0.6, w=0.1, r=0.9, show_info=False)
                best_solution, best_fit, fit_history = algo.run()


            end_processing_time = time.process_time()
            end_pref_time = time.perf_counter()
            fit_list.append(best_fit)
            cpu_times_list.append(end_processing_time - start_processing_time)
            run_times_list.append(end_pref_time - start_pref_time)
            # print("-----------------------------------")
            # print("name {},fun {}, dim {}, time {}/{}".format(name,func_name, problem_size, time_no + 1, run_times))
            # print('best fit:', best_fit)
            # i added
            # print('best solution:', best_solution)

        std = np.std(fit_list)
        mean = np.mean(fit_list)
        best = np.min(fit_list)
        worst = np.max(fit_list)
        avg_cpu_time = np.mean(cpu_times_list)
        avg_run_time = np.mean(run_times_list)
        out =  {
            'function': str(func_name),
            'dim': problem_size,
            'algo': name,
            'mean': mean,
            'std': std,
            'best': best,
            'worst': worst,
            'avg_cpu_time': avg_cpu_time,
            'avg_run_time': avg_run_time,
            'fit_list': fit_list
        }
        return [best_solution, out]







