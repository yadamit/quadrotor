import numpy as np
import tensorflow as tf
from random import randint

state_dim = 13;
action_dim = 4;

sess = tf.Session()

# Critic Network
class Critic:
	def __init__(self, input_layer=17, hidden_layer=100, output_layer=1):
		self.input_layer = input_layer
		self.hidden_layer = hidden_layer
		self.output_layer = output_layer
		self.critic_input = tf.placeholder(tf.float32, shape=[None, input_layer])
		self.critic_W1 = tf.Variable(tf.truncated_normal([input_layer, hidden_layer]), name="critic_W1")
		self.critic_b1 = tf.Variable(tf.truncated_normal([hidden_layer]), name='critic_b1')
		self.critic_W2 = tf.Variable(tf.truncated_normal([hidden_layer, output_layer]), name='critic_W2')
		self.critic_b2 = tf.Variable(tf.truncated_normal([output_layer]), name='critic_b2')

		self.critic_h1 = tf.nn.sigmoid(tf.add(tf.matmul(self.critic_input, self.critic_W1), self.critic_b1))
		self.critic_Q_value = tf.add(tf.matmul(self.critic_h1, self.critic_W2), self.critic_b2)

		# target
		self.target_input = tf.placeholder(tf.float32, shape=[None, input_layer])
		self.target_W1 = tf.Variable(tf.truncated_normal([input_layer, hidden_layer]), name="target_critic_W1")
		self.target_b1 = tf.Variable(tf.truncated_normal([hidden_layer]), name='target_critic_b1')
		self.target_W2 = tf.Variable(tf.truncated_normal([hidden_layer, output_layer]), name='target_critic_W2')
		self.target_b2 = tf.Variable(tf.truncated_normal([output_layer]), name='target_critic_b2')

		self.target_h1 = tf.nn.sigmoid(tf.add(tf.matmul(self.target_input, self.target_W1), self.target_b1))
		self.target_Q_value = tf.add(tf.matmul(self.target_h1,self.target_W2), self.target_b2)

	def initialize_params(self):
		sess.run(tf.initialize_all_variables())
		# Copy params in target network params
		sess.run(self.target_W1.assign(self.critic_W1))
		sess.run(self.target_b1.assign(self.critic_b1))
		sess.run(self.target_W2.assign(self.critic_W2))
		sess.run(self.target_b2.assign(self.critic_b2))

	def get_target_value(self, actor, state, reward, gamma):
		target_action = actor.get_target_action(state)
		state_action = tf.stack([state, target_action], axis=1)
		target_value = sess.run(self.target_Q_value, feed_dict={self.target_input:state_action})
		return reward + gamma * target_value;

	def get_critic_output(self, state_action):
		Q_value = sess.run(self.critic_Q_value,feed_dict={self.critic_input:state_action})

# Actor Network
class Actor:
	def __init__(self, input_layer=13, hidden_layer=100, output_layer=4):
		self.input_layer = input_layer
		self.hidden_layer = hidden_layer
		self.output_layer = output_layer
		self.actor_input = tf.placeholder(tf.float32, shape=[None, input_layer])
		self.actor_W1 = tf.Variable(tf.truncated_normal([input_layer, hidden_layer]), name="actor_W1")
		self.actor_b1 = tf.Variable(tf.truncated_normal([hidden_layer]), name='actor_b1')
		self.actor_W2 = tf.Variable(tf.truncated_normal([hidden_layer, output_layer]), name='actor_W2')
		self.actor_b2 = tf.Variable(tf.truncated_normal([output_layer]), name='actor_b2')

		self.actor_h1 = tf.nn.sigmoid(tf.add(tf.matmul(self.actor_input, self.actor_W1), self.actor_b1))
		self.actor_action = tf.add(tf.matmul(self.actor_h1, self.actor_W2), self.actor_b2)

		# target
		self.target_input = tf.placeholder(tf.float32, shape=[None, input_layer])
		self.target_W1 = tf.Variable(tf.truncated_normal([input_layer, hidden_layer]), name="target_actor_W1")
		self.target_b1 = tf.Variable(tf.truncated_normal([hidden_layer]), name='target_actor_b1')
		self.target_W2 = tf.Variable(tf.truncated_normal([hidden_layer, output_layer]), name='target_actor_W2')
		self.target_b2 = tf.Variable(tf.truncated_normal([output_layer]), name='target_actor_b2')

		self.target_h1 = tf.nn.sigmoid(tf.add(tf.matmul(self.target_input, self.target_W1), self.target_b1))
		self.target_action = tf.add(tf.matmul(self.target_h1,self.target_W2), self.target_b2)

	def initialize_params(self):
		sess.run(tf.initialize_all_variables())
		# Copy params in target network params
		sess.run(self.target_W1.assign(self.actor_W1))
		sess.run(self.target_b1.assign(self.actor_b1))
		sess.run(self.target_W2.assign(self.actor_W2))
		sess.run(self.target_b2.assign(self.actor_b2))

	def select_action(self, state):
		action = sess.run(self.actor_action,feed_dict={self.actor_input:state})
		return action

	def get_target_action(self, state):
		tar_action = sess.run(self.target_action, feed_dict={self.target_input: state});


class Replay:
	max_replay_size = 10000
	batch_size = 32
	def __init__(self):
		self.replay_buffer = None;

	def store_transition(self, old_state, action, reward, new_state):
		if self.replay_buffer.shape[0]>self.max_replay_size:
			self.replay_buffer = self.replay_buffer[1000:]
		tmp = np.concatenate((old_state,action))
		tmp = np.concatenate((tmp, reward))
		tmp = np.concatenate((tmp,new_state))
		self.replay_buffer = tmp if self.replay_buffer is None else np.append(self.replay_buffer, tmp, axis=0)
		self.replay_buffer.append(tmp)

	def select_random_batch(self):
		tmp = [randint(0,self.replay_buffer.shape[0]-1) for p in range(self.batch_size)]
		random_batch = self.replay_buffer[tmp]
		return random_batch







critic = Critic(state_dim+action_dim,100,1)
actor = Actor(state_dim,100,4)
critic.initialize_params()
actor.initialize_params()

replay = Replay()

num_episodes = 5
num_time_steps = 10
for epoch in range(num_episodes):
	# reset the environment and recieve initial state
	state = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1])
	# state=state.reshape(1, 13)
	for t in range(num_time_steps):
		action = actor.select_action(state.reshape(1,13))
		action = action[0] #action was a matrix, now it is an np.array(4,)
		# execute this action and recieve new_state,reward
		new_state = np.array([2,2,2,2,2,2,2,2,2,2,2,2,2])
		# new_state = new_state.reshape(1,13)
		reward = [3]
		reward = np.array(reward)
		replay.store_transition(state, action, reward, new_state)
		state = new_state 

		# select a random batch from replay_buffer
		batch = replay.select_random_batch()
		# batch = np.array(batch)

		# Q_values = critic.get_critic_output(np.concatenate((batch[:,0], batch[:,1])))







# exec(open("DDPG.py").read())