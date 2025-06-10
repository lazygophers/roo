package main

import (
	"github.com/lazygophers/log"
	"github.com/lazygophers/utils"
	"github.com/lazygophers/utils/candy"
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

	Groups []string `yaml:"groups,omitempty" validate:"required"`
	Source string   `yaml:"source,omitempty" validate:"required"`
}

func main() {
	models := make([]*CustomModel, 0)

	err := filepath.WalkDir("./custom_models_split", func(path string, d fs.DirEntry, err error) error {
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

		err = utils.Validate(&m)
		if err != nil {
			log.Errorf("err:%v", err)
			return err
		}

		models = append(models, &m)

		return nil
	})
	if err != nil {
		log.Errorf("err:%v", err)
		return
	}

	models = candy.SortUsing(models, func(a, b *CustomModel) bool {
		if a.Slug == "nexuscore" {
			return true
		}

		if b.Slug == "nexuscore" {
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
