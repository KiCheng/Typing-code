#include <iostream>
#include <cstring>
#include <climits>
#include <cstdio>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <queue>
#include <stack>
#include <map>
#include <set>
#include<algorithm>
using namespace std;


struct node {
	int val, x, y;
}a[100];

int visx[100], visy[100];

vector<node> all;
int ans = INT_MAX;
vector<node> final_ans;

void dfs(int now, int num) {
	if (num == 6) {
		int sum = 0;
		for (auto x : all) {
			sum += x.val;
		}
		double avg = double(sum) / 6.0;
		double var = 0;
		for (auto x : all) {
			var += double((double(x.val) - avg) * (double(x.val) - avg));
		}
		cout << var << endl;
		if (var <= ans) {
			final_ans.clear();
			for (auto x : all) {
				final_ans.push_back(x);
			}
			ans = var;
		}
		return;
	}
	for (int i = now + 1; i <= 76; i++) {
		node now_node = a[i];
		if (visx[now_node.x] || visy[now_node.x])
			continue;
		if (visx[now_node.y] || visy[now_node.y])
			continue;
		
		all.push_back(now_node);
		visx[now_node.x] = 1;
		visy[now_node.x] = 1;
		visx[now_node.y] = 1;
		visy[now_node.y] = 1;
		
		dfs(i, num + 1);

		all.pop_back();
		visx[now_node.x] = 0;
		visy[now_node.y] = 0;
		visx[now_node.y] = 0;
		visy[now_node.y] = 0;
	}
}

int main() {
	FILE* stream1;
	freopen_s(&stream1, "./out.txt", "r", stdin);
	for (int i = 1; i <= 76; i++) {
		cin >> a[i].x >> a[i].y >> a[i].val;
	}
	visx[1], visx[10], visx[13], visx[21], visx[22], visx[27] = 1;
	visy[1], visy[10], visy[13], visy[21], visy[22], visy[27] = 1;
	dfs(0, 0);
	cout << ans << endl;
	for (auto x : final_ans) {
		cout << x.x << " " << x.y << " " << x.val << endl;
	}
	return 0;
}