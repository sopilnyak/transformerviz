<template>
  <div class="container">
    <form v-on:submit.prevent="onSumbit" action="#" method="post" class="form">
      <select v-model="model" class="modelSelect">
        <option>BERT</option>
        <option>GPT-2</option>
        <option>XLNet</option>
        <option>XLM</option>
        <option>RoBERTa</option>
        <option>ALBERT</option>
      </select>
      <input v-model="source" placeholder="Source sentence" class="textInput" />
      <input v-model="target" placeholder="Target sentence" class="textInput" />
      <button type="submit" class="submitButton">Submit</button>
    </form>
    <svg
      ref="heads"
      :height="height"
      :width="width"
      class="visualization"
    ></svg>
  </div>
</template>

<script>
import * as d3 from "d3";
import test from "./test";

export default {
  name: "AttentionHead",
  data() {
    return {
      model: "BERT",
      source: "the cat sat on the mat",
      target: "the cat lay on the rug",
      width: 1100,
      height: 600,
      textBoxWidth: 120,
      textBoxHeight: 30,
      attentionBoxWidth: 30,
      textPadding: 20,
      centerWidth: 200,
      fontSize: 20,
      colorMap: d3.scaleOrdinal(d3.schemeTableau10),
      numHeads: 12,
      activeTokenIndex: -1,
      activeTokenLocation: "left",
      data: {}
    };
  },

  mounted() {
    this.data = test;
    this.renderVizualization();
  },

  watch: {
    activeTokenIndex: function() {
      this.onActiveTokenUpdate();
    },
    activeTokenLocation: function() {
      this.onActiveTokenUpdate();
    }
  },

  methods: {
    sliceDimension(index, dim) {
      let attentionMap = [];
      if (dim == 2) {
        this.data.attention.forEach(head => {
          let headAttention = [];
          head.forEach(source => {
            headAttention.push(source[index]);
          });
          attentionMap.push(headAttention);
        });
      } else {
        this.data.attention.forEach(head => {
          attentionMap.push(head[index]);
        });
      }
      return attentionMap;
    },

    transpose(array) {
      return array[0].map((col, i) => array.map(row => row[i]));
    },

    zip(a, b) {
      return a.map(function(e, i) {
        return [e, b[i]];
      });
    },

    displayAttentions(container, xOffset) {
      if (this.activeTokenIndex == -1) {
        return;
      }

      // (n_heads, source_len)
      let attentionMap = this.sliceDimension(
        this.activeTokenIndex,
        this.activeTokenLocation == "left" ? 1 : 2
      );

      // (source_len, n_heads)
      let attentionMapTransposed = this.transpose(attentionMap);
      let local = d3.local();
      let vue = this;

      container
        .append("g")
        .selectAll("g")
        .data(attentionMapTransposed)
        .enter()
        .append("g")
        .selectAll("rect")
        .data(function(d, i) {
          local.set(this, i);
          return d;
        })
        .enter()
        .append("rect")
        .classed("attentionRect", true)
        .attr("x", (d, i) => xOffset + i * this.attentionBoxWidth)
        .attr("y", function() {
          return local.get(this) * vue.textBoxHeight;
        })
        .attr("width", this.attentionBoxWidth)
        .attr("height", this.textBoxHeight)
        .attr("fill", (d, i) => this.colorMap(i))
        .style("opacity", d => d);

      let line_container = container.append("g");
      line_container
        .selectAll("g")
        .data(attentionMap)
        .enter()
        .append("g")
        .classed("attentionHeadLine", true)
        .selectAll("line")
        .data(d => d)
        .enter()
        .append("line")
        .classed("attentionLine", true);
    },

    displayText(container, text, xOffset) {
      let tokenContainer = container
        .append("g")
        .selectAll("g")
        .data(text)
        .enter()
        .append("g");

      let tokenRectContainer = tokenContainer
        .append("rect")
        .classed("background", true)
        .style("opacity", 0.3)
        .attr("fill", "lightgray")
        .attr("x", xOffset)
        .attr("y", (d, i) => i * this.textBoxHeight)
        .attr("width", this.textBoxWidth)
        .attr("height", this.textBoxHeight);

      tokenContainer
        .append("text")
        .text(d => d)
        .attr("font-size", this.fontSize + "px")
        .style("cursor", "default")
        .attr("x", xOffset)
        .attr("y", (d, i) => i * this.textBoxHeight)
        .style("text-anchor", container.attr("id") == "left" ? "end" : "start")
        .attr(
          "dx",
          container.attr("id") == "left"
            ? this.textBoxWidth - this.fontSize / 2
            : this.fontSize / 2
        )
        .attr("dy", this.fontSize);

      tokenContainer
        .on("mouseover", (d, tokenIndex) => {
          this.activeTokenIndex = tokenIndex;
          this.activeTokenLocation = container.attr("id");
          tokenRectContainer.style("opacity", function(d, i) {
            return i == tokenIndex ? 0.7 : 0.3;
          });
        })
        .on("mouseleave", () => {
          this.activeTokenIndex = -1;
          this.activeTokenLocation = container.attr("id");
          tokenRectContainer.style("opacity", 0.3);
        });
    },

    onActiveTokenUpdate() {
      // Clear attention map
      let container = d3.select(
        "#" + (this.activeTokenLocation == "left" ? "right" : "left")
      );
      container.selectAll(".attentionRect").style("display", "none");
      // Clear attention lines
      container.selectAll(".attentionHeadLine").style("display", "none");
      if (this.activeTokenIndex == -1) {
        return;
      }

      let xOffset = 0;
      if (this.activeTokenLocation == "left") {
        xOffset =
          this.attentionBoxWidth * this.numHeads +
          this.centerWidth +
          this.textBoxWidth;
      }
      this.displayAttentions(container, xOffset);

      container
        .selectAll(".attentionHeadLine")
        .selectAll(".attentionLine")
        .attr("y1", (d, i) => {
          if (this.activeTokenLocation == "left") {
            return (
              this.activeTokenIndex * this.textBoxHeight +
              this.textBoxHeight / 2
            );
          } else {
            return i * this.textBoxHeight + this.textBoxHeight / 2;
          }
        })
        .attr("x1", this.attentionBoxWidth * this.numHeads + this.textBoxWidth)
        .attr("y2", (d, i) => {
          if (this.activeTokenLocation == "left") {
            return i * this.textBoxHeight + this.textBoxHeight / 2;
          } else {
            return (
              this.activeTokenIndex * this.textBoxHeight +
              this.textBoxHeight / 2
            );
          }
        })
        .attr("x2", this.attentionBoxWidth * this.numHeads + this.centerWidth)
        .attr("stroke-width", 3)
        .attr("stroke", (d, i) => "#cccccc")
        .attr("opacity", d => d)
        .attr("stroke-opacity", d => d);
    },

    renderVizualization() {
      let svg = d3.select(this.$refs.heads);

      let left = svg.append("svg:g").attr("id", "left");
      let leftTextOffset = this.attentionBoxWidth * this.numHeads;
      this.displayText(left, this.data.source, leftTextOffset);

      let right = svg.append("svg:g").attr("id", "right");
      let rightOffset = leftTextOffset + this.centerWidth;
      this.displayText(right, this.data.target, rightOffset);
    },

    onSumbit() {
      let url = `http://localhost:8888/?model=${this.model}&source=${this.source}&target=${this.target}`;
      let xhr = new XMLHttpRequest();
      xhr.onload = xhr.onerror = () => {
        if (xhr.status == 200) {
          response = JSON.parse(xhr.responseText);
          this.data = test;
          this.renderVizualization();
        } else {
          alert("error");
        }
      };
      xhr.open("GET", url, true /* async */);
      xhr.send(null);
    }
  }
};
</script>

<style scoped>
.form {
  margin: 2em;
}

.modelSelect {
  height: 1.8em;
  width: 6em;
  padding-left: 0.4em;
  font-size: 20px;
  margin: 0.5em;
}

.textInput {
  height: 1.5em;
  width: 20em;
  padding-left: 0.4em;
  font-size: 20px;
  margin: 0.5em;
}

.submitButton {
  width: 5em;
  height: 1.5em;
  font-size: 20px;
  margin: 0.5em;
}

.visualization {
  margin: 0 auto;
}
</style>
