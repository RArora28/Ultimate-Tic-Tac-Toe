import sys
import random
import signal
import time
import copy
class pplayer:

    def __init__(self):
        self.block = [ [ 0 for i in xrange(0,4) ] for j in xrange(0,4) ]
        self.hash_block = [ [ 0 for i in xrange(0,4) ] for j in xrange(0,4) ]
        self.heuristic_table = {}
        self.heuristic_table[0] = [0,0,0,0,0,0]
        self.zobrist_block = []
        pw = 1
        for i in xrange(0,32):
            self.zobrist_block.append(pw)
            pw *= 2
        self.zobrist_board = []
        self.hash_board = 0
        for i in xrange(0,512):
            self.zobrist_board.append(random.randint(0, 170141183460469231731687303715884105728L))
        self.cellsweight = [[16,10,10,16],[10,16,16,10],[10,16,16,10],[16,10,10,16]]
        self.dp = {}
        self.considered_possibilities = []

    def hash(self):
        for i in xrange(0,4):
            for j in xrange(0,4):
                x = 0
                result = 0
                for k in xrange(0,4):
                    for l in xrange(0,4):
                        curr = self.local_board.board_status[4 * i + k][4 * j + l]
                        if curr == self.player:
                            result = result ^ self.zobrist_block[x * 2 + 1]
                        elif curr == self.opponent:
                            result = result ^ self.zobrist_block[x * 2 + 0]
                        x += 1

                self.hash_block[i][j] = result


    def heur_uttt(self):
        score = 0
        for i in xrange(0,4):
            for j in xrange(0,4):
                if self.local_board.block_status[i][j] == self.player:
                    score += self.cellsweight[i][j]
                elif self.local_board.block_status[i][j] == self.opponent:
                    score -= self.cellsweight[i][j] 

            if self.local_board.block_status[i].count(self.opponent) == 0:
                cnt = self.local_board.block_status[i].count(self.player)
                if cnt == 2 :
                    score += 15
                elif cnt == 3 :
                    score += 40
            col = [ x[i] for x in self.local_board.block_status ]
            if col.count(self.opponent) == 0:
                cnt = col.count(self.player)
                if cnt == 2:
                    score += 15
                elif cnt == 3:
                    score += 40

            if self.local_board.block_status[i].count(self.player) == 0:
                cnt = self.local_board.block_status[i].count(self.opponent)
                if cnt == 2 :
                    score -= 15
                elif cnt == 3 :
                    score -= 40
            col = [ x[i] for x in self.local_board.block_status ]
            if col.count(self.player) == 0:
                cnt = col.count(self.opponent)
                if cnt == 2:
                    score -= 15
                elif cnt == 3:
                    score -= 40
        maindiagonal = []
        for i in xrange(0,4):
            maindiagonal.append(self.local_board.block_status[i][i])
        if maindiagonal.count(self.opponent) == 0:
            cnt = maindiagonal.count(self.player)
            if cnt == 2:
                score += 15
            elif cnt == 3:
                score += 40
        if maindiagonal.count(self.player) == 0:
            cnt = maindiagonal.count(self.opponent)
            if cnt == 2:
                score -= 15
            elif cnt == 3:
                score -= 40
        otherdiagonal = []
        for i in xrange(0,4):
            otherdiagonal.append(self.local_board.block_status[3 - i][i])
        if otherdiagonal.count(self.opponent) == 0:
            cnt = otherdiagonal.count(self.player)
            if cnt == 2:
                score += 15
            elif cnt == 3:
                score += 40
        if otherdiagonal.count(self.player) == 0:
            cnt = otherdiagonal.count(self.opponent)
            if cnt == 2:
                score -= 15
            elif cnt == 3:
                score -= 40
        return score

    def heur_block1(self):
        score = 0
        bonus = 0
        openmove = 0
        if self.local_board.block_status[self.last_move[0] / 4][self.last_move[1] / 4] != '-':
            if self.local_board.board_status[self.last_move[0]][self.last_move[1]] == self.player:
                score += 20
                openmove = 20
            else:
                score -= 20
                openmove = -20
        for i in xrange(0,4):
            for j in xrange(0,4):
                if self.local_board.block_status[i][j] != '-':
                    continue
                center = 0
                tmpbonus = 0
                tmpscore = score
                if i >= 1 and i <= 2 and j >= 1 and j <= 2:
                    center = 1
                if i == 0 and (j==0 or j==3) :
                    center = 1
                if i == 3 and (j==0 or j==3) :
                    center = 1
                if self.hash_block[i][j] in self.heuristic_table:
                    score += self.heuristic_table[self.hash_block[i][j]][1]
                    if center:
                        bonus += self.heuristic_table[self.hash_block[i][j]][3]
                    continue
                for k in range(4):
                    for l in range(4):
                        self.block[k][l] = self.local_board.board_status[4 * i + k][4 * j + l]

                for k in xrange(0,4):    
                    if self.block[k].count(self.opponent) == 0:
                        cnt = self.block[k].count(self.player)
                        if cnt == 2:
                            score += 1.2
                            tmpbonus += 0.4
                        elif cnt == 3:
                            score += 3.5
                            tmpbonus += 0.4
                    
                    col = [ x[k] for x in self.block ]
                    if col.count(self.opponent) == 0:
                        cnt = col.count(self.player)
                        if cnt == 2:
                            score += 1.2
                            tmpbonus += 0.4
                        elif cnt == 3:
                            score += 3.5
                            tmpbonus += 0.4
                
                maindiagonal = []
                for k in xrange(0,4):
                    maindiagonal.append(self.block[k][k])
                if maindiagonal.count(self.opponent) == 0:
                    cnt = maindiagonal.count(self.player)
                    if cnt == 2:
                        score += 1.2
                        tmpbonus += 0.4
                    elif cnt == 3:
                        score += 3.5
                        tmpbonus += 0.4
                otherdiagonal = []
                for k in xrange(0,4):
                    otherdiagonal.append(self.block[3 - k][k])
                if otherdiagonal.count(self.opponent) == 0:
                    cnt = otherdiagonal.count(self.player)
                    if cnt == 2:
                        score += 1.2
                        tmpbonus += 0.4
                    elif cnt == 3:
                        score += 3.5
                        tmpbonus += 0.4
                if center :
                    bonus += tmpbonus
                self.heuristic_table[self.hash_block[i][j]] = [-1000,score-openmove-tmpscore,0,tmpbonus]
        
        return score + bonus

    def heur_block2(self):
        score = 0
        bonus = 0
        for i in xrange(0,4):
            for j in xrange(0,4):
                if self.local_board.block_status[i][j] != '-':
                    continue
                center = 0
                tmpbonus = 0
                tmpscore = score
                if i >= 1 and i <= 2 and j >= 1 and j <= 2:
                    center = 1
                if i == 0 and (j==0 or j==3) :
                    center = 1
                if i == 3 and (j==0 or j==3) :
                    center = 1
                if self.heuristic_table[self.hash_block[i][j]][0] != -1000:
                    score += self.heuristic_table[self.hash_block[i][j]][0]
                    if center:
                        bonus += self.heuristic_table[self.hash_block[i][j]][2]
                    continue

                for k in range(4):
                    for l in range(4):
                        self.block[k][l] = self.local_board.board_status[4 * i + k][4 * j + l]

                for k in xrange(0,4):    
                    if self.block[k].count(self.player) == 0:
                        cnt = self.block[k].count(self.opponent)
                        if cnt == 2:
                            score += 1.2
                            tmpbonus += 0.4
                        elif cnt == 3:
                            score += 3.5
                            tmpbonus += 0.4

                    col = [ x[k] for x in self.block ]
                    if col.count(self.player) == 0:
                        cnt = col.count(self.opponent)
                        if cnt == 2:
                            score += 1.2
                            tmpbonus += 0.4
                        elif cnt == 3:
                            score += 3.5
                            tmpbonus += 0.4
                
                maindiagonal = []
                for k in xrange(0,4):
                    maindiagonal.append(self.block[k][k])
                if maindiagonal.count(self.player) == 0:
                    cnt = maindiagonal.count(self.opponent)
                    if cnt == 2:
                        score += 1.2
                        tmpbonus += 0.4
                    elif cnt == 3:
                        score += 3.5
                        tmpbonus += 0.4
                
                otherdiagonal = []
                for k in xrange(0,4):
                    otherdiagonal.append(self.block[3 - k][k])
                if otherdiagonal.count(self.player) == 0:
                    cnt = otherdiagonal.count(self.opponent)
                    if cnt == 2:
                        score += 1.2
                        tmpbonus += 0.4
                    elif cnt == 3:
                        score += 3.5
                        tmpbonus += 0.4
                if center :
                    bonus += tmpbonus
                self.heuristic_table[self.hash_block[i][j]][0] = score - tmpscore
                self.heuristic_table[self.hash_block[i][j]][2] = tmpbonus

        return score + bonus

    def alphabeta(self, depth, alpha, beta, maximini, old_move):
        terminal_status = self.local_board.find_terminal_state()
        if depth == 0 or terminal_status[0] != 'CONTINUE' :
            if terminal_status[0] == self.player :
                return 360
            if terminal_status[0] != self.player and terminal_status[1] == 'WON':
                return -360
            if terminal_status[1] == 'DRAW':
                score = 0
                for i in xrange(0,4):
                    for j in xrange(0,4):
                        if self.local_board.block_status[i][j] == self.player:
                            score += 13
                        if self.local_board.block_status[i][j] == self.opponent:
                            score -= 20
                return score
            return self.heur_uttt()+self.heur_block1()-self.heur_block2()

        elif maximini:
            v = -1000
            if (depth, old_move) in self.considered_possibilities :
                for x in self.dp[(depth, old_move)]:
                    valid_moves.append(x)

                self.dp[(depth, old_move)].clear()
                self.considered_depths.erase((depth, old_move))
                valid_moves = sorted(valid_moves, reverse = True)   
            else :
                valid_moves = self.local_board.find_valid_move_cells(old_move)

            # valid_moves = self.local_board.find_valid_move_cells(old_move)
            # random.shuffle(valid_moves)
            
            cutoff = 0

            for valid_move in valid_moves:
                if cutoff == 0:
                    self.local_board.update(old_move, valid_move, self.player)
                    self.hash_block[valid_move[0] / 4][valid_move[1] / 4] ^= self.zobrist_block[2 * (valid_move[0] % 4 * 4 + valid_move[1] % 4) + 1]
                    self.hash_board ^= self.zobrist_board[2 * (valid_move[0] * 16 + valid_move[1]) + 1]
                    self.last_move = valid_move
                    new_v = self.alphabeta(depth - 1, alpha, beta, 0, valid_move)

                    # self.dp[(depth, old_move)].append((new_v, valid_move))
                    if (depth, old_move) not in self.considered_possibilities :
                        t = (depth, old_move)
                        self.considered_possibilities.append(t)

                    self.local_board.board_status[valid_move[0]][valid_move[1]] = '-'
                    x = valid_move[0] / 4
                    y = valid_move[1] / 4
                    self.local_board.block_status[x][y] = '-'
                    self.hash_block[x][y] ^= self.zobrist_block[2 * (valid_move[0] % 4 * 4 + valid_move[1] % 4) + 1]
                    self.hash_board ^= self.zobrist_board[2 * (valid_move[0] * 16 + valid_move[1]) + 1]
                    if new_v > v:
                        if self.level == depth:
                            self.best_move = valid_move
                        v = new_v
                    alpha = max(alpha, v)
                    if beta <= alpha:
                        cutoff = 1
                else :
                    pass
                    # self.dp(depth, old_move).append((1000, valid_move))
            return v
        else:
            v = 1000
            valid_moves = self.local_board.find_valid_move_cells(old_move)
            for valid_move in valid_moves:
                player_ply = 'x' if self.player == 'o' else 'x'
                self.local_board.update(old_move, valid_move, self.opponent)
                self.hash_block[valid_move[0] / 4][valid_move[1] / 4] ^= self.zobrist_block[2 * (valid_move[0] % 4 * 4 + valid_move[1] % 4) + 0]
                self.hash_board ^= self.zobrist_board[2 * (valid_move[0] * 16 + valid_move[1]) + 0]
                self.last_move = valid_move
                v = min(v, self.alphabeta(depth - 1, alpha, beta, 1, valid_move))
                self.local_board.board_status[valid_move[0]][valid_move[1]] = '-'
                x = valid_move[0] / 4
                y = valid_move[1] / 4
                self.local_board.block_status[x][y] = '-'
                self.hash_block[x][y] ^= self.zobrist_block[2 * (valid_move[0] % 4 * 4 + valid_move[1] % 4) + 0]
                self.hash_board ^= self.zobrist_board[2 * (valid_move[0] * 16 + valid_move[1]) + 0]
                beta = min(beta, v)
                if beta <= alpha:
                    break

            return v

    def signal_handler(self, signum, frame):
        raise Exception('Timed out!')

    def move(self, board, old_move, flag):
    	print old_move
        self.player = flag
        self.opponent = 'x' if self.player == 'o' else 'o'
        saved = copy.deepcopy(board)
        if old_move != (-1, -1):
            self.hash_block[old_move[0] / 4][old_move[1] / 4] ^= self.zobrist_block[2 * (old_move[0] % 4 * 4 + old_move[1] % 4) + 0]
        self.local_board = board
        signal.signal(signal.SIGALRM, self.signal_handler)
        self.last_move = (0, 0)
        signal.alarm(15)
        self.hash()
        self.dp = {}
        self.considered_possibilities = []

        try:
            for i in xrange(3, 100):
                self.level = i
                print i
                self.alphabeta(i, -1000, 1000, 1, old_move)
                best = self.best_move
                self.local_board = saved
                print i

        # except Exception as msg:
    	except Exception as e:
			print 'Exception occurred ', e
			print 'Traceback printing ', sys.exc_info()
			pass
        self.hash_block[best[0] / 4][best[1] / 4] ^= self.zobrist_block[2 * (best[0] % 4 * 4 + best[1] % 4) + 1]
        return best
