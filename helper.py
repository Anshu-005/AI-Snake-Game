import matplotlib.pyplot as plt

plt.ion()

def plot(scores, mean_scores):
    try:
        plt.clf()
        plt.title('Training Progress')
        plt.xlabel('Number of Games')
        plt.ylabel('Score')
        plt.plot(scores, label='Score', color='#1f77b4')
        plt.plot(mean_scores, label='Mean Score', color='#ff7f0e')
        plt.ylim(ymin=0)
        if len(scores) > 0:
            plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
            plt.text(len(mean_scores) - 1, mean_scores[-1], f"{mean_scores[-1]:.2f}")
        plt.legend(loc='upper left')
        plt.show(block=False)
        plt.pause(0.05)
    except Exception:
        pass

