package main

import (
	"embed"
	"github.com/lazygophers/log"
	"github.com/lazygophers/utils"
	"github.com/lazygophers/utils/candy"
	"github.com/lazygophers/utils/stringx"
	"gopkg.in/yaml.v3"
	"io/fs"
	"os"
	"path/filepath"
)

type CustomModel struct {
	Slug string `yaml:"slug,omitempty" validate:"required"`
	Name string `yaml:"name,omitempty" validate:"required"`

	RoleDefinition string `yaml:"roleDefinition,omitempty" validate:"required"`
	WhenToUse      string `yaml:"whenToUse,omitempty" validate:"required"`

	CustomInstructions string `yaml:"customInstructions,omitempty" validate:"required"`

	Groups []string `yaml:"groups,omitempty" validate:"required,dive,oneof=read edit browser mcp command"`
	//Source string   `yaml:"source,omitempty" validate:"required"`
}

//go:embed docs/initializer.txt
var embedFs embed.FS

func main() {
	models := make([]*CustomModel, 0)

	memoryInitializer, err := embedFs.ReadFile("docs/initializer.txt")
	if err != nil {
		log.Errorf("err:%v", err)
		return
	}

	var brainModel *CustomModel

	err = filepath.WalkDir("./custom_models_split", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			log.Errorf("err:%v", err)
			return err
		}

		if filepath.Ext(path) != ".yaml" {
			return nil
		}

		log.Infof("try handle %s", path)

		file, err := os.Open(path)
		if err != nil {
			log.Errorf("err:%v", err)
			return err
		}
		defer file.Close()

		var m CustomModel
		err = yaml.NewDecoder(file).Decode(&m)
		if err != nil {
			log.Errorf("err:%v", err)
			return err
		}

		m.Groups = []string{
			"read",
			"edit",
			"browser",
			"mcp",
			"command",
		}
		m.CustomInstructions = stringx.ToString(memoryInitializer) + "\n\n" + m.CustomInstructions

		err = utils.Validate(&m)
		if err != nil {
			log.Errorf("err:%v", err)
			return err
		}

		models = append(models, &m)

		if m.Slug == "brain" {
			brainModel = &m
		}

		return nil
	})
	if err != nil {
		log.Errorf("err:%v", err)
		return
	}

	{
		brainModel.CustomInstructions += "\n\ncustom_models:"

		for _, model := range models {
			if model.Slug == "brain" {
				continue
			}

			brainModel.CustomInstructions += "\n\t- 模式: " + model.Slug
			brainModel.CustomInstructions += "\n\t  使用场景: " + model.WhenToUse
		}
	}

	models = candy.SortUsing(models, func(a, b *CustomModel) bool {
		if a.Slug == "brain" {
			return true
		}

		if b.Slug == "brain" {
			return false
		}

		return a.Slug < b.Slug
	})

	file, err := os.OpenFile("custom_models.yaml", os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		log.Errorf("err:%v", err)
		return
	}
	defer file.Close()

	// 添加排序逻辑

	encoder := yaml.NewEncoder(file)
	encoder.SetIndent(2)
	err = encoder.Encode(map[string]any{
		"customModes": models,
	})
	if err != nil {
		log.Errorf("err:%v", err)
		return
	}
}
